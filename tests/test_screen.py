from cotaudit.data.screen import screen_ml

OPTS = ["a", "b", "c", "d"]


def q(text, options=OPTS):
    return {"question": text, "options": options}


def test_clean_translation_passes():
    en = q("Which of the following cranial nerves is related to the sense of smell?")
    ml = q("താഴെപ്പറയുന്ന തലയോട്ടി നാഡികളിൽ ഏതാണ് ഘ്രാണശക്തിയുമായി ബന്ധപ്പെട്ടിരിക്കുന്നത്?")
    assert screen_ml(en, ml) == []


def test_dropped_passage_is_flagged():
    en = q("This question refers to the following information.\n" + "Long passage text. " * 30
           + "\nWhich of the following best describes the passage?")
    ml = q("ഈ ഭാഗത്തെ ഏറ്റവും നന്നായി വിവരിക്കുന്നത് ഏത്?")
    reasons = screen_ml(en, ml)
    assert any("shortened" in r for r in reasons)
    assert any("collapsed" in r for r in reasons)


def test_inline_formula_kept_on_one_line_passes():
    en = q("A researcher tests the model:\n\n$y_t = b_1 + u_t$\n\nWhich would be the unrestricted RSS?")
    ml = q("ഒരു ഗവേഷകൻ ഈ മോഡൽ പരിശോധിക്കുന്നു: $y_t = b_1 + u_t$ നിയന്ത്രണമില്ലാത്ത RSS ഏതായിരിക്കും?")
    assert screen_ml(en, ml) == []


def test_lost_logic_symbols_are_flagged_but_approx_tilde_is_not():
    en = q("Construct a truth table for the argument. P ⊃ Q / ~P")
    ml = q("വാദത്തിനായി ഒരു സത്യപട്ടിക നിർമ്മിക്കുക.")
    assert any("⊃" in r and "~" in r for r in screen_ml(en, ml))
    en2 = q("It had an angular size of about 0.5 degrees (~30 pixels).")
    ml2 = q("അതിന് ഏകദേശം 0.5 ഡിഗ്രി (30 പിക്സൽ) കോണുണ്ടായിരുന്നു.")
    assert screen_ml(en2, ml2) == []


def test_untranslated_repetition_and_options():
    en = q("The algorithm below is used to simulate the results of flipping a coin four times.")
    assert "question left untranslated" in screen_ml(en, q(en["question"]))
    loop = q("ഭൗതികശാസ്ത്രം, " * 12)
    assert "repetition loop" in screen_ml(q("x " * 10), loop)
    assert "missing or empty options" in screen_ml(q("x"), q("ക", ["a", "", "c", "d"]))
