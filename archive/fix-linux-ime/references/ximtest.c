/* Minimal XIM test client mimicking winit's input path:
 * XOpenIM -> XCreateIC(style from winit's preference order) ->
 * event loop: XFilterEvent + Xutf8LookupString.
 * Prints everything it receives. Type pinyin + space in the window. */
#include <stdio.h>
#include <string.h>
#include <locale.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>

static XIM im;
static XIC ic;

int main(void) {
    Display *d = XOpenDisplay(NULL);
    if (!d) { printf("no display\n"); return 1; }
    printf("locale: %s\n", setlocale(LC_ALL, ""));
    if (!XSupportsLocale()) { printf("XSupportsLocale FAILED\n"); }
    printf("XSetLocaleModifiers: %s\n", XSetLocaleModifiers("@im=fcitx"));

    im = XOpenIM(d, NULL, NULL, NULL);
    if (!im) { printf("XOpenIM FAILED\n"); return 1; }

    XIMStyles *styles = NULL;
    XGetIMValues(im, XNQueryInputStyle, &styles, NULL);
    printf("IM supports %d styles:\n", styles ? (int)styles->count_styles : 0);
    for (int i = 0; styles && i < (int)styles->count_styles; i++)
        printf("  style[%d] = 0x%lx\n", i, styles->supported_styles[i]);

    /* winit preference: PreeditCallbacks|StatusNothing, else PreeditNothing|StatusNothing */
    XIMStyle chosen = 0;
    for (int i = 0; styles && i < (int)styles->count_styles; i++) {
        XIMStyle s = styles->supported_styles[i];
        if ((s & (XIMPreeditCallbacks|XIMStatusNothing)) == (XIMPreeditCallbacks|XIMStatusNothing))
            { chosen = s; break; }
    }
    if (!chosen)
        for (int i = 0; styles && i < (int)styles->count_styles; i++) {
            XIMStyle s = styles->supported_styles[i];
            if ((s & (XIMPreeditNothing|XIMStatusNothing)) == (XIMPreeditNothing|XIMStatusNothing))
                { chosen = s; break; }
        }
    if (!chosen) { printf("no usable style!\n"); return 1; }
    printf("chosen style: 0x%lx\n", chosen);

    Window w = XCreateSimpleWindow(d, DefaultRootWindow(d), 100, 100, 500, 300, 1,
                                   BlackPixel(d, 0), WhitePixel(d, 0));
    XSelectInput(d, w, KeyPressMask | KeyReleaseMask | FocusChangeMask | ExposureMask);
    XStoreName(d, w, "XIM TEST");
    ic = XCreateIC(im, XNInputStyle, chosen, XNClientWindow, w, XNFocusWindow, w, NULL);
    if (!ic) { printf("XCreateIC FAILED\n"); return 1; }
    XMapWindow(d, w);
    XFlush(d);
    printf("window ready - click it, Ctrl+Space, type pinyin, press SPACE. Ctrl+C to quit.\n");

    XEvent ev;
    while (1) {
        XNextEvent(d, &ev);
        if (XFilterEvent(&ev, None)) {
            if (ev.type == KeyPress)
                printf("[filtered KeyPress serial=%lu]\n", ev.xkey.serial);
            continue;
        }
        if (ev.type == FocusIn) { XSetICFocus(ic); printf("[focus in]\n"); }
        if (ev.type == FocusOut) { XUnsetICFocus(ic); printf("[focus out]\n"); }
        if (ev.type == Expose) { XFlush(d); }
        if (ev.type == KeyPress) {
            char buf[64] = {0};
            KeySym ks = 0; Status st = 0;
            int n = Xutf8LookupString(ic, &ev.xkey, buf, sizeof(buf)-1, &ks, &st);
            printf("[KeyPress kc=%d] status=%d count=%d utf8=\"", ev.xkey.keycode, (int)st, n);
            for (int i = 0; i < n; i++) putchar((unsigned char)buf[i] & 0xff ? buf[i] : '?');
            printf("\" bytes:", n);
            for (int i = 0; i < n; i++) printf(" %02x", (unsigned char)buf[i]);
            printf(" keysym=0x%lx\n", ks);
            if (n > 0 && st == XLookupChars) printf("  *** GOT COMMIT TEXT ***\n");
            if (ks == XK_Escape) break;
        }
    }
    XCloseIM(im); XCloseDisplay(d);
    return 0;
}
