---
name: myme-qml-ui
description: Use when modifying QML files in crates/myme-ui/qml/ in MyMe. Covers Theme system, page patterns, Sidebar navigation, animations, component conventions.
---
# QML UI Specialist

## Scope
Files: `crates/myme-ui/qml/` (13939 lines QML), `qml.qrc`
Key files:
- `Main.qml` — ApplicationWindow root: sidebar + StackView
- `Theme.qml` — Singleton: Warm Forge palette, typography, spacing
- `Icons.qml` — Singleton: Phosphor icon unicode constants
- `AppContext.qml` — Singleton: global state (currentPage, sidebarExpanded)
- `components/Sidebar.qml` — Persistent collapsible sidebar (220px/60px)
- `pages/NotePage.qml` — Template for data-driven pages with model polling
- `qml.qrc` — Resource bundle (ALL QML files must be listed here)

## Key Interfaces

**Theme.qml** (Warm Forge):
```qml
// Colors
property color primary: isDark ? "#e5a54b" : "#c08832"
property color background: isDark ? "#1a1a1a" : "#faf8f5"
property color surface: isDark ? "#242424" : "#ffffff"
property color text: isDark ? "#e8e0d4" : "#2c2418"
property color textSecondary: isDark ? "#a09080" : "#8c7a68"
// Spacing
property int spacingSm: 5; property int spacingMd: 10; property int spacingLg: 20
// Cards
property int cardRadius: 10; property int cardPadding: 20; property int buttonRadius: 8
// Mode
property string mode: "auto"  // "light", "dark", "auto"
property bool isDark: mode === "dark" || (mode === "auto" && systemDark)
```

**Page template** (all pages follow):
```qml
import QtQuick; import QtQuick.Layouts; import QtQuick.Controls; import ".."
Page {
    id: root
    ModelName { id: theModel }
    Timer { interval: 100; running: root.visible; repeat: true; onTriggered: theModel.poll_channel() }
    ColumnLayout { anchors.fill: parent; anchors.margins: Theme.spacingLg; spacing: Theme.spacingLg }
}
```

**Navigation** (`Main.qml`):
```qml
RowLayout {
    Sidebar { id: sidebar; onNavigate: (page) => loadPage(page) }
    StackView { id: pageStack; /* push/pop pages */ }
}
function loadPage(page) { AppContext.currentPage = page; pageStack.replace(null, pageComponent) }
```

**Keyboard shortcuts**: Ctrl+1-8 nav, Ctrl+B sidebar toggle, Ctrl+, settings

## Architecture

Layout: `RowLayout` with persistent Sidebar (sibling, NOT inside StackView) + StackView. Sidebar width: 220px expanded, 60px collapsed. StackView slide-fade transitions: opacity 0→1 + x-offset 20→0, 200ms OutCubic.

Model interaction: QML instantiates QObject model → Timer polls `poll_channel()` while visible → model properties update → QML bindings react automatically.

Singletons (Theme, Icons, AppContext) registered in `qmldir` as `pragma Singleton`. Import via `import ".."` from pages.

## Common Mistakes
- **Forgot qml.qrc** — new QML files must be added to `qml.qrc` or they won't be found at runtime
- **Snake_case invocables** — call `model.fetch_data()` not `model.fetchData()`. cxx-qt preserves Rust naming.
- **Sidebar inside StackView** — sidebar must be RowLayout sibling, not StackView child. Otherwise it reloads on every page change.
- **Timer not stopped** — use `running: root.visible` to stop polling when page is not shown
- **Missing `import ".."`** — pages must import parent directory to access Theme/Icons singletons
- **Binding loops** — avoid bidirectional property bindings. Use `onTextChanged` handlers instead.
- **Large list perf** — for 1000+ items, use ListView delegates (not Repeater) for virtualization

## Staggered Animation Pattern
```qml
// In list delegates:
opacity: 0
Component.onCompleted: fadeIn.start()
SequentialAnimation {
    id: fadeIn
    PauseAnimation { duration: index * 30 }
    ParallelAnimation {
        NumberAnimation { target: delegate; property: "opacity"; to: 1; duration: 200; easing.type: Easing.OutCubic }
        NumberAnimation { target: delegate; property: "y"; from: delegate.y + 8; to: delegate.y; duration: 200; easing.type: Easing.OutCubic }
    }
}
```

## Card Styling Pattern
```qml
Rectangle {
    radius: Theme.cardRadius
    color: Theme.surface
    border.color: Theme.isDark ? "#ffffff08" : "#00000008"
    border.width: 1
    // Content with Theme.cardPadding margins
}
```

## Testing Patterns
- QML changes don't need rebuild — just restart the app
- Visual testing: manual inspection after each change
- Theme: test both dark/light modes (toggle in Settings)
- No automated QML tests — rely on Rust-side service tests + manual UI verification

## Related Specs
- `docs/specs/qml-ui.md` — Full Theme palette values, page inventory, component details, qml.qrc structure
