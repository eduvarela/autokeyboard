---
name: Control Panel Utility
colors:
  surface: '#081425'
  surface-dim: '#081425'
  surface-bright: '#2f3a4c'
  surface-container-lowest: '#040e1f'
  surface-container-low: '#111c2d'
  surface-container: '#152031'
  surface-container-high: '#1f2a3c'
  surface-container-highest: '#2a3548'
  on-surface: '#d8e3fb'
  on-surface-variant: '#bcc9c6'
  inverse-surface: '#d8e3fb'
  inverse-on-surface: '#263143'
  outline: '#879391'
  outline-variant: '#3d4947'
  surface-tint: '#6bd8cb'
  primary: '#6bd8cb'
  on-primary: '#003732'
  primary-container: '#29a195'
  on-primary-container: '#00302b'
  inverse-primary: '#006a61'
  secondary: '#93ccff'
  on-secondary: '#003351'
  secondary-container: '#3198dc'
  on-secondary-container: '#002c47'
  tertiary: '#ffb59a'
  on-tertiary: '#591c02'
  tertiary-container: '#d27956'
  on-tertiary-container: '#4f1700'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#89f5e7'
  primary-fixed-dim: '#6bd8cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#005049'
  secondary-fixed: '#cce5ff'
  secondary-fixed-dim: '#93ccff'
  on-secondary-fixed: '#001d31'
  on-secondary-fixed-variant: '#004b73'
  tertiary-fixed: '#ffdbce'
  tertiary-fixed-dim: '#ffb59a'
  on-tertiary-fixed: '#370e00'
  on-tertiary-fixed-variant: '#773215'
  background: '#081425'
  on-background: '#d8e3fb'
  surface-variant: '#2a3548'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-base:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-bold:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0em
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  mono-value:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 12px
  panel-padding: 20px
---

## Brand & Style

This design system is built for precision, reliability, and high-performance utility. It targets power users who require a dependable tool for automation, emphasizing a "Control Panel" aesthetic that balances industrial technicality with modern software refinement. 

The visual direction is **Technical Minimalism**. It borrows the organized, grid-heavy structure of physical hardware consoles and translates them into a digital interface. The goal is to evoke a sense of "professional equipment" through organized information density, clear functional grouping, and high-contrast status indicators. The UI should feel like a specialized piece of kit—stable, responsive, and authoritative.

## Colors

The palette is centered around a "Deep Teal" primary color, chosen for its professional and technical associations. While the system supports both light and dark modes, the primary experience is optimized for a dark "Console" environment to reduce eye strain during long sessions.

- **Primary (Teal):** Used for the most critical actions, such as "Start Auto-Clicker" and active state toggles.
- **Secondary (Blue):** Used for navigational elements and secondary configuration buttons.
- **Neutral:** A range of Slate grays provides the foundation. In dark mode, these create tonal depth; in light mode, they provide crisp structural definition.
- **Functional Colors:** High-saturation greens and reds are reserved strictly for "Running" vs. "Stopped" statuses, mimicking LED indicators on physical hardware.

## Typography

This design system utilizes a dual-font approach to reinforce the technical aesthetic.

1. **Space Grotesk (Headlines & Labels):** A geometric sans-serif with a technical, futuristic edge. It is used for titles and all-caps labels to mimic the etched text found on control boards.
2. **Inter (Body & UI):** A highly legible, neutral sans-serif used for all functional text, settings, and descriptions to ensure clarity and professional tone.

Numerical values in input fields should utilize a monospaced-adjacent feel by using the medium weight of Space Grotesk, ensuring that changing numbers don't cause layout jitter.

## Layout & Spacing

The layout follows a **Modular Grid** philosophy. Elements are contained within clearly defined "Panels" or "Modules" that group related functions (e.g., Timing Settings, Key Sequence, Global Controls).

- **Grid:** A standard 8px rhythm for component spacing, with a 4px sub-grid for tighter internal element alignment (like icons next to text).
- **Structure:** Content should be organized into a single-column or two-column layout depending on window width.
- **Alignment:** Consistent 20px padding inside all primary panels. Use 12px gutters between adjacent panels to create a "slotted" look.

## Elevation & Depth

To achieve the "Control Panel" look, this design system avoids heavy, ambient shadows in favor of **Tonal Layering** and **Inner Definition**.

- **Surface Levels:** The background uses the darkest neutral shade. Panels sit one level above with a slightly lighter hex code and a subtle 1px border.
- **Insets:** Input fields and list items should appear "recessed" into the panels using subtle inner shadows or darker background fills.
- **Active State:** Elements that are "On" should appear to glow slightly, utilizing a soft outer glow in the primary teal color rather than a traditional drop shadow.
- **Borders:** Use low-contrast borders (1px) to define edges between elements without adding visual clutter.

## Shapes

The shape language is **Structured and Geometric**. 

- **Corners:** A base radius of 4px (`rounded-sm`) is used for buttons and inputs to maintain a crisp, industrial feel. 
- **Containers:** Larger panels use 8px (`rounded-md`) to soften the overall application frame while remaining professional.
- **Avoidance:** Avoid fully rounded "pill" shapes, as they lean too far into consumer-social aesthetics. Every shape should feel intentional and machined.

## Components

### Buttons
- **Action Buttons:** Large, solid Teal backgrounds with white text for primary triggers like "Start."
- **Secondary Buttons:** Outlined or subtle gray backgrounds for "Add Key" or "Clear List."
- **Toggle Switches:** Use a hardware-inspired sliding toggle with high-contrast color indicators for active states.

### Input Fields (The "Dial" Aesthetic)
- **Interval Inputs:** Numeric inputs should have a fixed suffix (e.g., "ms" or "sec") anchored to the right side of the field.
- **Recessed Style:** Fields should have a darker background than the panel they sit on, creating a "well" effect.

### Sequence List
- **Draggable Rows:** Each item in the key sequence list must have a clear "grip" icon for reordering.
- **List Items:** Use subtle horizontal separators and include a quick-action "delete" icon that appears on hover.

### Status Indicator
- A prominent "LED" style circle in the header that pulses slowly when the auto-clicker is active.

### Chips
- Use small, monochromatic chips for keyboard modifiers (e.g., [Ctrl], [Shift]) with a monospaced font weight.