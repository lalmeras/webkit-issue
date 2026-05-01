import argparse

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Soup', '3.0')
gi.require_version('WebKit', '6.0')
from gi.repository import GLib, Gio, Gdk, Gtk, Adw, WebKit

class Application(Adw.Application):
    def __init__(self, issue):
        if issue:
            WebKit.NetworkSession.get_default()
        super().__init__(application_id="com.github.lalmeras.WebkitIssue")
    
    def do_activate(self):
        window = Adw.ApplicationWindow(application=self)
        webview = WebKit.WebView()
        webview.load_uri("https://w3.org")
        window.set_content(webview)
        window.present()

def run():
    parser = argparse.ArgumentParser(prog='webkit-issue')
    parser.add_argument("--issue", action="store_true", default=False)
    args = parser.parse_args()
    app = Application(args.issue)
    app.run()