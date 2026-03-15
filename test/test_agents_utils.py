import pytest
from unittest.mock import MagicMock
from finrobot.agents.utils import order_trigger, instruction_trigger

# --- Fixtures ---

@pytest.fixture
def mock_sender_factory():
    """Factoría de mocks para simular diferentes estados de agentes emisores."""
    def _create_mock(name="assistant", content=None, has_name=True, has_last_message=True):
        if content is None and not has_name and not has_last_message:
            return None

        sender = MagicMock()
        
        if has_name:
            sender.name = name
        else:
            del sender.name

        if has_last_message:
            if isinstance(content, dict) or content is None or content is False:
                # Permite inyectar tipos incorrectos para pruebas defensivas
                sender.last_message.return_value = content
            else:
                sender.last_message.return_value = {"content": content}
        else:
            del sender.last_message
        return sender
    return _create_mock


# --- SECCIÓN 1: Tests para Order Trigger ---

class TestOrderTrigger:
    @pytest.mark.parametrize(
        "sender_name, sender_content, target_name, target_pattern, expected",
        [
            # Happy path
            ("assistant", "execute the buy order", "assistant", "buy", True),

            # Caminos negativos (Nombre o contenido incorrecto)
            ("user", "execute the buy order", "assistant", "buy", False),
            ("assistant", "execute the sell order", "assistant", "buy", False),

            # Insensibilidad a Mayúsculas/Minúsculas
            ("ASSISTANT", "EXECUTE THE BUY ORDER", "assistant", "buy", True),
            ("AsSiStAnT", "eXeCuTe ThE bUy OrDeR", "aSsIsTaNt", "BuY", True),

            # Insensibilidad a espacios en blanco y saltos de línea
            ("  assistant  ", "    execute the buy order   ", " assistant ", " buy ", True),
            ("\nassistant\n", "\nexecute the buy order\n", "assistant", "buy", True),

            # Programación defensiva - Datos mal formados
            ("assistant", None, "assistant", "buy", False),
            ("assistant", {"other_key": "value"}, "assistant", "buy", False),
            ("assistant", {"content": 123}, "assistant", "buy", False),
            (123, "buy order", "123", "buy", False),

            # Caracteres de Regex tratados como texto plano (Escape)
            ("assistant", "execute the b*y order?", "assistant", "b*y", True),
            ("assistant", "execute the bbby order", "assistant", "b*y", False),
        ]
    )
    def test_order_trigger_scenarios(
        self, mock_sender_factory, sender_name, sender_content, target_name, target_pattern, expected
    ):
        sender = mock_sender_factory(name=sender_name, content=sender_content)
        assert order_trigger(sender, name=target_name, pattern=target_pattern) is expected

    def test_order_trigger_none_sender(self):
        assert order_trigger(None, name="assistant", pattern="buy") is False


# --- SECCIÓN 2: Tests para Instruction Trigger ---

class TestInstructionTrigger:
    @pytest.mark.parametrize(
        "last_message_return, expected",
        [
            # Éxito: cadena exacta presente
            ({"content": "instruction & resources saved to /path/to/file"}, True),
            # Sensibilidad a mayúsculas (según lógica de master)
            ({"content": "INSTRUCTION & RESOURCES SAVED TO /path/to/file"}, False),
            # El trigger es parte de una cadena más larga
            ({"content": "The final instruction & resources saved to the disk successfully."}, True),
            # Variaciones de espacios
            ({"content": "   instruction & resources saved to   "}, True),

            # Fallos: contenido ausente o tipos incorrectos
            ({"content": "some other message"}, False),
            ({"other_key": "instruction & resources saved to"}, False),
            ("instruction & resources saved to", False),  # Retorna string en lugar de dict
            (None, False),
            ({}, False),
            ({"content": 123}, False),
        ]
    )
    def test_instruction_trigger_scenarios(self, mock_sender_factory, last_message_return, expected):
        sender = mock_sender_factory(content=last_message_return)
        assert instruction_trigger(sender) == expected

    def test_instruction_trigger_missing_method(self):
        class BadSender: pass
        assert instruction_trigger(BadSender()) is False

    def test_instruction_trigger_not_callable(self):
        class WeirdSender: last_message = "not a callable"
        assert instruction_trigger(WeirdSender()) is False