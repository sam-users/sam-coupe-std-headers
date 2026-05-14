# samcoupestdheaders <!-- omit from toc -->

This project contains a set of standard header files for SAM Coupé
Z80 assembly language development. They're meant to make your life easier by defining a bunch of common constants once, so that you don't have to look them up online.

## Contents <!-- omit from toc -->

- [Files](#files)
- [Coding Style](#coding-style)
- [Conventions](#conventions)
  - [`_MASK` suffix on constants](#_mask-suffix-on-constants)
  - [`_BASE` suffix on constants](#_base-suffix-on-constants)
  - [`_MIN`/`_MAX` suffixes on constants](#_min_max-suffixes-on-constants)
  - ["Dead" values](#dead-values)
  - [`_H` and `_L` suffixes for upper/lower parts of values](#_h-and-_l-suffixes-for-upperlower-parts-of-values)
  - [Obsolete values](#obsolete-values)
  - [Read-only, Write-Only, and Read/Write markers](#read-only-write-only-and-readwrite-markers)
  - [`_MALIGN` and `_LEFTSHIFT` suffixes](#_malign-and-_leftshift-suffixes)
  - [`_BIX` suffixes](#_bix-suffixes)
- [Spelling](#spelling)
- [Copyright and Licensing](#copyright-and-licensing)

## Files

Following is the list of files included in this repository, and what they're for.

| Filename | Description |
| -------- | ----------- |
| [allports.z80](allports.z80) | Master include that includes all of the other files. Include this in your program to make your life a little easier. |
| [base.z80](base.z80) | Ports needed by nearly every program (plus a few that didn't make sense to split out into their own file, like MIDI). |
| [colours.z80](colours.z80) | Helpful constants for standard color palette values. |
| [comms.z80](comms.z80) | Constants used by the SAM Coupé Serial and Printer interfaces. |
| [disk.z80](disk.z80) | Constants used by the Disk interfaces and controller chip (VL1772-02). |
| [joystick.z80](joystick.z80) | Constants used to map joystick entries to keyboard ports, including the ports to read so that you don't have to pull in the whole keyboard if you only want joystick support. |
| [keyboard.z80](keyboard.z80) | Constants used by the keyboard. |
| [lightpen.z80](lightpen.z80) | Lightpen support. |
| [sound.z80](sound.z80) | Constants and values used by the SAA-1099 sound chip. |

## Coding Style

- We use consistent casing for constants within a file. FIles ending in "_l.z80" are lowercase variants, without the_l. they're UPPERCASE.
- We use `_` for separators within constants. `SEE_WHAT_I_MEAN`?
- We use `lowercase.names:` with periods as separators for
  code labels.
- We use `lowercase` for assembly instructions.
- We use `UPPERCASE` for assembly directives (`EQU`, `DW`, `INCLUDE`, etc...)
- We provide US and UK English spelling variants. Where it makes sense to do so, they're provided in separate files. Usually, they're provided inline immediately below the UK variant.

## Conventions

### `_MASK` suffix on constants

We use `_MASK` to indicate a constant that can be `and`ed with a value to isolate it. Usually this is used when a port or
register contains multiple different ranges of bits for different functions.

**Example:**

```z80
in a,(BORDER)
and BORDER_COLOR_MASK
```

`_MASK` constants are only provided for values which cover 2 or more bits, not for single-bit values.

### `_BASE` suffix on constants

A suffix of `_BASE` on a constant is used to imply that it's the first in a range of values. To get the other values, you'd
add values to the top of it.

**Example:**

```z80
CLUT_BASE: EQU 248
PALETTE_4: EQU CLUT_BASE + (4*256)
```

### `_MIN`/`_MAX` suffixes on constants

`_MIN` implies the lowest value in a range.
`_MAX` implies the highest value in a range.

**Example:**

```z80
OCTAVE_MIN:    EQU 0
OCTAVE_MAX:    EQU 7
AMPLITUDE_MIN: EQU 0
AMPLITUDE_MAX: EQU 15
```

### "Dead" values

Some values are given even though they're going to be `or`ed into something, and they have the value of zero. This is so that you can be explicit about what you're doing, and spell it out.

(This kind of thing is an assemble-time operation; it won't cost anything at runtime).

**Example:**

```z80
DISK_CMD_WRITE_SECTOR_MARK_VALID: EQU 0

; ... later ...

ld a,DISK_CMD_WRITE_SECTOR | DISK_CMD_WRITE_SECTOR_MARK_VALID
OUT (DISK_0_CMD),A
```

**Note:** Sometimes we'll just define things for symmetry.

### `_H` and `_L` suffixes for upper/lower parts of values

If a constant ends with `_H`, it is usually intended to be used as the high
register (A8-A15) during IO operations. There will usually be another version
of the constant name without the `_H` suffix for use as a 16-bit register
value.

**Example:**

Use the `_H` version like this:

```z80
ld a,COMMS_MR_H
in a,(COMMS_0_BASE)
```

... whereas you'd use the version without `_H` like this:

```z80
ld bc,COMMS_0_BASE + COMMS_MR
in a,(c)
```

Similar to the `_H` suffix, `_L` indicates the lower part of a 16-bit value.

### Obsolete values

Some things in the SAM Coupé spec have been obsoleted over the years. We won't delete these, but we will mark them as obsolete in the source, and in some cases comment them out as necessary.

**Example:**

```z80
STATUS_LINE_INT:    EQU %00000001
; While this was named the MOUSE interrupt, it's currently used exclusively by
; the SAM Comms Interface for RS232 controller interrupts.
; The MOUSE doesn't use this, and instead has its own counters that are read out
; serially by the user.
STATUS_COMMS_INT:   EQU %00000010
;STATUS_MOUSE_INT:  EQU %00000010 ; OBSOLETE
STATUS_MIDI_IN_INT: EQU %00000100
```

### Read-only, Write-Only, and Read/Write markers

In the documentation you'll find markers that indicate whether a port supports read or write operation. These values can be:

|Marker|Meaning|
|------|-------|
|`[RO]`|Read Only|
|`[WO]`|Write Only|
|`[R/W]`|Read/Write|

### `_MALIGN` and `_LEFTSHIFT` suffixes

The `_MALIGN` and `_LEFTSHIFT` suffixes are used to indicate what you have to `M`ultiply a value to `ALIGN` it to the correct
slot (in other words, `MALIGN`). `_LEFTSHIFT` shows how many times you must shift a value to the left to align it to the slot
indicated by the name to the left of the suffix. (**Warning:** This _could_ be zero).

These may be more useful in macro-expansions than in code. in code you might be better off understanding the bit alignment
and accounting for that yourself via look-up tables, shift instructions, or other methods to map to the correct alignment.

### `_BIX` suffixes

Any value suffixed with `_BIX` is a bit-index. This is the number of times you have to shift a value, or a value that can
be used with `BIT n,r`, `SET n,r` and `RES n,r` instructions.

**Example:**

```z80
ld bc,(RTC_HOURS_10S)
in e,(c)
bit RTC_HOURS_AMPM_BIX,E
jr nz,clock.afternoon
```

## Spelling

We now provide UK and US english spellings in the headers where there are differences (only COLOR/COLOUR so far).

## Copyright and Licensing

 The provided source code and documentation are Copyright &copy; 2023 Simon Cooke, and are licensed under the MIT license (see the [LICENSE](./LICENSE) file).

 In this release we've provided a lot of datasheets and other documentation. We'd like feedback on this - we could put
 these in a separate repository.

 Also, if people object to us redistributing their copyrighted work, let us know, and we'll stop redistributing it and
 provide an end-user mechanism to download it from the official site instead - although many of these parts are obsolete
 and datasheets are often intended to be redistributed broadly.
