﻿# -*- coding: utf-8 -*-
"""
Text normalization
"""
import re
import warnings

from pythainlp import thai_above_vowels as above_v
from pythainlp import thai_below_vowels as below_v
from pythainlp import thai_follow_vowels as follow_v
from pythainlp import thai_lead_vowels as lead_v
from pythainlp import thai_tonemarks as tonemarks


_PHANTOM_CHARS = f"{above_v}{below_v}{tonemarks}\u0e3a\u0e4c\u0e4d\u0e4e"
_RE_REMOVE_PHANTOMS = re.compile(f"^[{_PHANTOM_CHARS}]+")

_ZERO_WIDTH_CHARS = "\u200c\u200b"
_RE_REMOVE_ZERO_WIDTHS = re.compile(f"[{_ZERO_WIDTH_CHARS}]+")

_REORDER_PAIRS = [
    ("\u0e40\u0e40", "\u0e41"),  # Sara E + Sara E -> Sara Ae
    (
        f"([{tonemarks}\u0e4c]+)([{above_v}{below_v}]+)",
        "\\2\\1",
    ),  # TONE/Thanthakhat + ABV/BLW VOWEL -> ABV/BLW VOWEL + TONE/Thanthakhat
    (
        f"\u0e4d([{tonemarks}]*)\u0e32",
        "\\1\u0e33",
    ),  # Nikhahit + TONEMARK + Sara Aa -> TONEMARK + Sara Am
    (
        f"([{follow_v}]+)([{tonemarks}]+)",
        "\\2\\1",
    ),  # FOLLOW VOWEL + TONEMARK+ -> TONEMARK + FOLLOW VOWEL
]

# VOWELS + Phinthu, Thanthakhat, Nikhahit, Yamakkan
_NOREPEAT_CHARS = (
    f"{follow_v}{lead_v}{above_v}{below_v}\u0e3a\u0e4c\u0e4d\u0e4e"
)
_NOREPEAT_PAIRS = list(
    zip([f"({ch}[ ]*)+" for ch in _NOREPEAT_CHARS], _NOREPEAT_CHARS)
)

_RE_TONEMARKS = re.compile(f"[{tonemarks}]+")


def _last_char(matchobj):  # to be used with _RE_NOREPEAT_TONEMARKS
    return matchobj.group(0)[-1]


def remove_phantom(text: str) -> str:
    """
    Remove a char that may have been accidentally typed at the text beginning.
    """
    return _RE_REMOVE_PHANTOMS.sub("", text)


def remove_tonemarks(text: str) -> str:
    """
    Remove Thai tonemarks from the text.

    There are 4 tonemarks indicating 4 tones as follows:

        * Down tone (Thai: ไม้เอก  _่ )
        * Falling tone  (Thai: ไม้โท  _้ )
        * High tone (Thai: ไม้ตรี  ​_๊ )
        * Rising tone (Thai: ไม้จัตวา _๋ )

    :param str text: text in Thai language
    :return: text without Thai tonemarks
    :rtype: str

    :Example:
    ::

        from pythainlp.util import delete_tone

        delete_tone('สองพันหนึ่งร้อยสี่สิบเจ็ดล้านสี่แสนแปดหมื่นสามพันหกร้อยสี่สิบเจ็ด')
        # output: สองพันหนึงรอยสีสิบเจ็ดลานสีแสนแปดหมืนสามพันหกรอยสีสิบเจ็ด
    """
    return _RE_TONEMARKS.sub("", text)


def remove_zw(text: str) -> str:
    """
    Remove zero-width characters.
    """
    return _RE_REMOVE_ZERO_WIDTHS.sub("", text)


def normalize(text: str) -> str:
    """
    Normalize Thai text with normalizing rules as follows:

        * Remove redundant vowels and tonemarks
        * Subsitute "เ" + "เ" with "แ"

    :param str text: thai text to be normalized
    :return: normalized Thai text according to the fules
    :rtype: str

    :Example:
    ::

        from pythainlp.util import normalize

        normalize('สระะน้ำ')
        # output: สระน้ำ

        normalize('เเปลก')
        # output: แปลก

        normalize('นานาาา')
        # output: นานา
    """
    text = remove_zw(text)

    for pair in _REORDER_PAIRS:
        text = re.sub(pair[0], pair[1], text)
    for pair in _NOREPEAT_PAIRS:
        text = re.sub(pair[0], pair[1], text)

    # remove repeating tonemarks, use last tonemark
    text = _RE_TONEMARKS.sub(_last_char, text)

    text = remove_phantom(text)

    return text


def delete_tone(text: str) -> str:
    """
    DEPRECATED: Please use remove_tonemarks().
    """
    return remove_tonemarks(text)
