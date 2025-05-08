# Azure Theme for Ttk
# Adapted from https://github.com/rdbende/Azure-ttk-theme

package provide azure 1.0

namespace eval ttk::theme::azure {
    # General settings
    set colors(-bg) {#333333}      ;# Main background
    set colors(-fg) {#ffffff}      ;# Main foreground (text)
    set colors(-primary) {#0078d7} ;# Primary color (e.g., accents, selection)
    set colors(-secondary) {#555555} ;# Secondary color (e.g., button backgrounds)
    set colors(-disabled) {#777777} ;# Disabled foreground
    set colors(-active) {#666666}   ;# Active/hover background for buttons
    set colors(-border) {#404040}   ;# Borders
    set colors(-inputbg) {#404040}  ;# Input field background
    set colors(-inputfg) {#ffffff}  ;# Input field foreground
    set colors(-selectbg) $colors(-primary) ;# Selected item background
    set colors(-selectfg) $colors(-fg)      ;# Selected item foreground
    set colors(-trough) $colors(-secondary) ;# Trough color for progressbar/scrollbar

    # Helper to create a layout with a border and padding
    proc ClamLayout {widget T element args} {
        set temática 0
        if {$T eq "TRadiobutton" || $T eq "TCheckbutton"} {
            set temática 1
        }
        ttk::style layout $widget.border {
            Widget.border -sticky nswe -border 1 -children {
                $widget.padding -sticky nswe -border $temática -padding ${args} -children {
                    $widget.$element -sticky nswe
                }
            }
        }
        eval ttk::style layout $T $widget.border
    }

    # Helper for button-like elements
    proc ButtonLayout {widget T element args} {
        ttk::style layout $T {
            $widget.highlight -sticky nswe -children {
                $widget.border -sticky nswe -border 1 -children {
                    $widget.padding -sticky nswe -padding ${args} -children {
                        $widget.focus -sticky nswe -children {
                            $widget.$element -sticky nswe
                        }
                    }
                }
            }
        }
    }

    # Define styles for widgets
    # --- General ---
    ttk::style theme create azure-dark -parent clam -settings {
        # Default settings for all widgets
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-border) \
            -troughcolor $colors(-trough) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -fieldbackground $colors(-inputbg) \
            -insertcolor $colors(-inputfg) \
            -font {"Segoe UI" 10}

        ttk::style map . \
            -background [list disabled $colors(-bg) active $colors(-active)] \
            -foreground [list disabled $colors(-disabled)] \
            -selectbackground [list !focus $colors(-selectbg) focus $colors(-selectbg)] \
            -selectforeground [list !focus $colors(-selectfg) focus $colors(-selectfg)]

        # --- TButton ---
        ttk::style configure TButton \
            -padding {10 5} \
            -background $colors(-secondary) \
            -foreground $colors(-fg) \
            -relief raised \
            -borderwidth 1
        ttk::style map TButton \
            -background [list active $colors(-active) pressed $colors(-primary) disabled $colors(-secondary)] \
            -foreground [list disabled $colors(-disabled)] \
            -relief [list pressed sunken !pressed raised]

        # --- TLabel ---
        ttk::style configure TLabel -padding {5 2} -background $colors(-bg) -foreground $colors(-fg)

        # --- TEntry ---
        ttk::style configure TEntry \
            -padding {5 5} \
            -background $colors(-inputbg) \
            -foreground $colors(-inputfg) \
            -insertcolor $colors(-inputfg) \
            -relief sunken \
            -borderwidth 1
        ttk::style map TEntry \
            -background [list readonly $colors(-secondary)] \
            -foreground [list readonly $colors(-disabled)] \
            -bordercolor [list focus $colors(-primary) !focus $colors(-border)]

        # --- TFrame ---
        ttk::style configure TFrame -background $colors(-bg)

        # --- TProgressbar ---
        ttk::style configure TProgressbar \
            -background $colors(-primary) \
            -troughcolor $colors(-trough) \
            -borderwidth 1 \
            -relief sunken
        ttk::style layout TProgressbar {
            Progressbar.trough -sticky nswe -children {
                Progressbar.pbar -sticky nswe
            }
        }
        ttk::style element create Progressbar.pbar from default
        ttk::style element create Progressbar.trough from default


        # --- TScrollbar ---
        ttk::style configure TScrollbar \
            -background $colors(-secondary) \
            -troughcolor $colors(-trough) \
            -relief flat \
            -arrowcolor $colors(-fg) \
            -arrowsize 14
        ttk::style map TScrollbar \
            -background [list active $colors(-active)] \
            -relief [list active flat]

        # --- TCombobox (Dropdown) ---
        ttk::style configure TCombobox \
            -padding 5 \
            -background $colors(-inputbg) \
            -foreground $colors(-inputfg) \
            -insertcolor $colors(-inputfg) \
            -arrowcolor $colors(-fg) \
            -arrowsize 15
        ttk::style map TCombobox \
            -background [list readonly $colors(-secondary) focus $colors(-inputbg)] \
            -fieldbackground [list readonly $colors(-secondary) focus $colors(-inputbg)] \
            -foreground [list readonly $colors(-disabled) focus $colors(-inputfg)] \
            -bordercolor [list focus $colors(-primary) !focus $colors(-border)] \
            -arrowcolor [list hover $colors(-primary)]

        # --- ttk::calendar (tkcalendar) specific styling if possible, often limited ---
        # This is a basic attempt, tkcalendar might not fully respect ttk themes for all parts
        ttk::style configure TCalendar \
            -background $colors(-bg) \
            -foreground $colors(-fg)
        ttk::style configure Calendar.Treeview -fieldbackground $colors(-inputbg) -background $colors(-inputbg)
        ttk::style map Calendar.Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]

        # --- ScrolledText (uses tk.Text, not ttk) ---
        # Styling for ScrolledText's Text widget needs to be done directly on the widget
        # or via option_add for tk.Text, as it's not a ttk widget.
        # Example: root.option_add("*Text.background", colors(-inputbg))
        #          root.option_add("*Text.foreground", colors(-inputfg))

        # --- Toplevel (for dialogs like date picker) ---
        # This is tricky as Toplevel is tk, not ttk.
        # We can try to set its background.
        # Example: top.configure(bg=colors(-bg)) in the pick_date method.
    }

    # Light theme variant (example)
    ttk::style theme create azure-light -parent clam -settings {
        ttk::style configure . \
            -background {#f0f0f0} \
            -foreground {#000000} \
            -bordercolor {#cccccc} \
            -troughcolor {#e0e0e0} \
            -selectbackground {#0078d7} \
            -selectforeground {#ffffff} \
            -fieldbackground {#ffffff} \
            -insertcolor {#000000} \
            -font {"Segoe UI" 10}

        ttk::style configure TButton \
            -padding {10 5} \
            -background {#e1e1e1} \
            -foreground {#000000} \
            -relief raised \
            -borderwidth 1
        ttk::style map TButton \
            -background [list active {#c0c0c0} pressed {#005a9e}]

        ttk::style configure TEntry \
            -padding {5 5} \
            -background {#ffffff} \
            -foreground {#000000} \
            -insertcolor {#000000} \
            -relief sunken \
            -borderwidth 1
        ttk::style map TEntry \
            -bordercolor [list focus {#0078d7}]

        ttk::style configure TProgressbar -background {#0078d7}
        ttk::style configure TLabel -background {#f0f0f0} -foreground {#000000}
        ttk::style configure TFrame -background {#f0f0f0}
    }
}

# Set the default theme to azure-dark if desired
# ttk::style theme use azure-dark
