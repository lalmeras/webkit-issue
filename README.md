# webkit-issue

This is a minimal test-case to exhibit a python / webkit issue.

If webkit code is called before Gtk application_id is set set, then WebKit is to load
and cache a fallback applicationID (`org.webkit.app-...`).

When application is packaged in a flatpak, it triggers a fatal failure when WebKit tries
to communicate its `sandbox-a11y-own-name` to flatpak portal (because flatpak rejects
the name if it does not start with the flatpak application name).

This issue may not be triggered:
* when application is launched from `$HOME/.var`, webkit `isFlatpakSpawnUsable` is false
  so flatpak portal is not called
* when application is launched with older runtime, applicationID is correctly computed.
  I suspect that WebKit changes its behavior about applicationID

This project exhibits all these behavior.

## Build

Python hatch used for build (https://hatch.pypa.io/).

```shell
# Build
hatch build
flatpak-builder --user --install --force-clean builddir com.github.lalmeras.WebkitIssue.json
```

## Usage

Application provides a `webkit-issue` command that just load a webkit WebView and display https://w3.org.

Use `--issue` flag to perform a `WebKit.NetworkSession.get_default()` call before Gtk application initialization.
It triggers the applicationID discovery that leads to a fatal failure with recent runtimes.

```shell
# run on host (python gobject and webkit needed; may be available on a gnome desktop)
# should works fine
hatch run webkit-issue
# should works fine (flatpak portal call is not performed)
hatch run webkit-issue --issue

# may fail depending on runtime and CWD; see use-cases
flatpak run com.github.lalmeras.WebkitIssue
```

`dbus-monitor` can be used to check what portal calls are performed. Depending on `$CWD`:

```shell
dbus-monitor "interface='org.freedesktop.portal.Flatpak'"
```

* a call with `echo` command is always performed when packaged in flatpak.
  It is the `isFlatpakSpawnUsable` check
* if `CWD=$HOME`: a second call is performed with the `sandbox-a11y-own-names` dict entry. This entry
  may contain `org.webkit.app-` (buggy) or `com.github.lalmeras.WebkitIssue.Sandboxed.WebProcess-` (fine)

## Use cases

**any runtime**

```shell
cd $HOME/.var
flatpak run --runtime=org.fedoraproject.Platform//f43 com.github.lalmeras.WebkitIssue
flatpak run --runtime=org.fedoraproject.Platform//f44 com.github.lalmeras.WebkitIssue
flatpak run --runtime=org.gnome.Platform//50 com.github.lalmeras.WebkitIssue
# Application starts successfully
# dbus-monitor: no sandbox-a11y-own-name field
```

**org.fedoraproject.Platform//f43**

```shell
cd $HOME
flatpak run --runtime=org.fedoraproject.Platform//f43 com.github.lalmeras.WebkitIssue
# Application starts successfully
# dbus-monitor: sandbox-a11y-own-name=com.github.lalmeras.WebkitIssue.Sandboxed.WebProcess-...
```

```shell
cd $HOME
flatpak run --runtime=org.fedoraproject.Platform//f43 com.github.lalmeras.WebkitIssue --issue
# Application starts successfully
# dbus-monitor: sandbox-a11y-own-name=com.github.lalmeras.WebkitIssue.Sandboxed.WebProcess-...
```

**org.fedoraproject.Platform//f44**

```shell
cd $HOME
flatpak run --runtime=org.fedoraproject.Platform//f44 com.github.lalmeras.WebkitIssue
# Application starts successfully
# dbus-monitor: sandbox-a11y-own-name=com.github.lalmeras.WebkitIssue.Sandboxed.WebProcess-...
```

```shell
cd $HOME
flatpak run --runtime=org.fedoraproject.Platform//f44 com.github.lalmeras.WebkitIssue --issue
# Application does not start: Portal call failed: Invalid sandbox a11y own name: ...
# dbus-monitor: sandbox-a11y-own-name=org.webkit.app-...
```

**org.gnome.Platform//50**

```shell
cd $HOME
flatpak run --runtime=org.gnome.Platform//50 com.github.lalmeras.WebkitIssue
# Application starts successfully
# dbus-monitor: sandbox-a11y-own-name=com.github.lalmeras.WebkitIssue.Sandboxed.WebProcess-...
```

```shell
cd $HOME
flatpak run --runtime=org.gnome.Platform//50 com.github.lalmeras.WebkitIssue --issue
# Application does not start: Portal call failed: Invalid sandbox a11y own name: ...
# dbus-monitor: sandbox-a11y-own-name=org.webkit.app-...
```

# References

See:
* Wike issue: https://github.com/hugolabe/Wike/issues/239
* applicationID loading and caching: https://github.com/WebKit/WebKit/blob/527346d57f8cc02763692c6b91a8a59dfbe62413/Source/WTF/wtf/glib/Application.cpp#L39
* dbus message sent with a11y-own-name: https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/Launcher/glib/FlatpakLauncher.cpp#L91
* isFlatpakSpawnUsable: https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/Launcher/glib/ProcessLauncherGLib.cpp#L60