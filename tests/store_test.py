from app.store import Store


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
    for key in result[0].keys():
        print(key, " --------- ", result[0][key])
    assert len(result) == 1

test_store_check_sequence_existing()