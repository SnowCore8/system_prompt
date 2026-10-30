/* Inject the current local time into supported Qoder hook events. */

#define _POSIX_C_SOURCE 200809L

#include <ctype.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#include <windows.h>
#endif

static const char *const EVENTS[] = {
    "SessionStart",   "UserPromptSubmit",  "PreToolUse",
    "PostToolUse",    "PostToolUseFailure", "SubagentStart",
    "Notification",   "CwdChanged",        "FileChanged",
};

static int is_space(char c) { return isspace((unsigned char)c); }

static char *read_stdin(size_t *len) {
    size_t cap = 4096, n = 0;
    char *buf = malloc(cap);
    if (!buf) return NULL;
    for (;;) {
        if (n == cap) {
            if (cap >= (size_t)1 << 20) break;
            cap *= 2;
            char *grown = realloc(buf, cap);
            if (!grown) {
                free(buf);
                return NULL;
            }
            buf = grown;
        }
        size_t got = fread(buf + n, 1, cap - n, stdin);
        n += got;
        if (got == 0) break;
    }
    if (ferror(stdin)) {
        free(buf);
        return NULL;
    }
    *len = n;
    return buf;
}

static size_t skip_ws(const char *s, size_t n, size_t i) {
    while (i < n && is_space(s[i])) i++;
    return i;
}

/* Read the top-level "hook_event_name" string from a JSON object. */
static int parse_event(const char *s, size_t n, char *out, size_t outsz) {
    size_t i = skip_ws(s, n, 0);
    if (i >= n || s[i] != '{') return 0;
    i++;
    int have_event = 0;
    int after_comma = 0;
    for (;;) {
        i = skip_ws(s, n, i);
        if (i < n && s[i] == '}') {
            if (after_comma) return 0;
            i++;
            break;
        }
        if (i >= n || s[i] != '"') return 0;
        after_comma = 0;

        size_t key_start = ++i;
        while (i < n && s[i] != '"') {
            if (s[i] == '\\' && i + 1 < n) i++;
            i++;
        }
        if (i >= n) return 0;
        size_t key_len = i - key_start;
        i++;

        i = skip_ws(s, n, i);
        if (i >= n || s[i] != ':') return 0;
        i = skip_ws(s, n, i + 1);
        if (i >= n) return 0;

        int is_target = key_len == 15 &&
                        memcmp(s + key_start, "hook_event_name", 15) == 0;

        if (s[i] == '"') {
            size_t value_start = ++i;
            while (i < n && s[i] != '"') {
                if (s[i] == '\\' && i + 1 < n) i++;
                i++;
            }
            if (i >= n) return 0;
            size_t value_len = i - value_start;
            i++;
            if (is_target) {
                if (value_len == 0 || value_len + 1 > outsz) return 0;
                memcpy(out, s + value_start, value_len);
                out[value_len] = '\0';
                have_event = 1;
            }
        } else {
            int depth = 0, in_string = 0;
            for (; i < n; i++) {
                char c = s[i];
                if (in_string) {
                    if (c == '\\' && i + 1 < n) {
                        i++;
                    } else if (c == '"') {
                        in_string = 0;
                    }
                    continue;
                }
                if (c == '"') {
                    in_string = 1;
                } else if (c == '{' || c == '[') {
                    depth++;
                } else if (c == '}' || c == ']') {
                    if (depth == 0) break;
                    depth--;
                } else if (c == ',' && depth == 0) {
                    break;
                }
            }
            if (i >= n) return 0;
        }

        i = skip_ws(s, n, i);
        if (i < n && s[i] == ',') {
            i++;
            after_comma = 1;
            continue;
        }
        if (i < n && s[i] == '}') {
            i++;
            break;
        }
        return 0;
    }
    if (skip_ws(s, n, i) != n) return 0;
    return have_event;
}

static int format_time(char *out, size_t outsz) {
    char zone[8] = "+00:00";
#ifdef _WIN32
    SYSTEMTIME local, utc;
    FILETIME local_ft, utc_ft;
    ULARGE_INTEGER local_ull, utc_ull;
    GetLocalTime(&local);
    GetSystemTime(&utc);
    if (!SystemTimeToFileTime(&local, &local_ft) ||
        !SystemTimeToFileTime(&utc, &utc_ft)) {
        return 0;
    }
    local_ull.LowPart = local_ft.dwLowDateTime;
    local_ull.HighPart = local_ft.dwHighDateTime;
    utc_ull.LowPart = utc_ft.dwLowDateTime;
    utc_ull.HighPart = utc_ft.dwHighDateTime;
    int offset_min =
        (int)(((long long)local_ull.QuadPart - (long long)utc_ull.QuadPart) /
              600000000LL);
    if (offset_min > 23 * 60 + 59) offset_min = 23 * 60 + 59;
    if (offset_min < -(23 * 60 + 59)) offset_min = -(23 * 60 + 59);
    int magnitude = offset_min < 0 ? -offset_min : offset_min;
    snprintf(zone, sizeof zone, "%c%02d:%02d", offset_min < 0 ? '-' : '+',
             magnitude / 60, magnitude % 60);
    return snprintf(out, outsz, "%04d-%02d-%02d %02d:%02d:%02d %s",
                    local.wYear, local.wMonth, local.wDay, local.wHour,
                    local.wMinute, local.wSecond, zone) > 0;
#else
    time_t now = time(NULL);
    struct tm local;
    if (!localtime_r(&now, &local)) return 0;
    char date[32];
    if (strftime(date, sizeof date, "%Y-%m-%d %H:%M:%S", &local) == 0) return 0;
    char raw_zone[8];
    if (strftime(raw_zone, sizeof raw_zone, "%z", &local) == 5 &&
        (raw_zone[0] == '+' || raw_zone[0] == '-')) {
        snprintf(zone, sizeof zone, "%.3s:%.2s", raw_zone, raw_zone + 3);
    }
    return snprintf(out, outsz, "%s %s", date, zone) > 0;
#endif
}

int main(void) {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    size_t len = 0;
    char *payload = read_stdin(&len);
    if (!payload) return 0;
    char event[32];
    int found = parse_event(payload, len, event, sizeof event);
    free(payload);
    if (!found) return 0;

    int supported = 0;
    for (size_t i = 0; i < sizeof EVENTS / sizeof *EVENTS; i++) {
        if (strcmp(EVENTS[i], event) == 0) {
            supported = 1;
            break;
        }
    }
    if (!supported) return 0;

    char timestamp[64];
    if (!format_time(timestamp, sizeof timestamp)) return 0;

    printf("{\"hookSpecificOutput\":{\"hookEventName\":\"%s\","
           "\"additionalContext\":\"当前时间：%s\"}}\n",
           event, timestamp);
    return 0;
}
