from app.store import Store


def test_initialize():
    store_instance = Store()
    store_instance.initialize()


def test_store_check_term_non_existing():
    store_instance = Store()
    result = store_instance.check_term("nichtexistierendeswort")
    assert result == False


def test_store_check_term_existing():
    store_instance = Store()
    result = store_instance.check_term("organisieren")
    assert result == True


def test_store_check_sequence_non_existing():
    store_instance = Store()
    result = store_instance.check_sequence(
        "nichtexistierendeswort in einer Sequence"
    )
    assert len(result) == 0


def test_store_check_sequence_existing():
    store_instance = Store()
    result = store_instance.check_sequence(
        "Prioritäten im Zusammenhang mit der Rohrleitungsintegrität weiterverfolgen"
    )
    assert len(result) == 1

