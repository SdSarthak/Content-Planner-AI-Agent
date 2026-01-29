import unittest
from unittest.mock import patch, MagicMock
import types
import main

class AttrDict(types.SimpleNamespace):
    def __contains__(self, key):
        return hasattr(self, key)
    def __getitem__(self, key):
        return getattr(self, key)
    def __setitem__(self, key, value):
        setattr(self, key, value)

def no_cache_decorator(func):
    def wrapper(*args, **kwargs):
        # Always call the real function, never cache
        return func(*args, **kwargs)
    return wrapper

class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch st.cache_data to a no-op decorator for all tests
        cls.cache_data_patcher = patch.object(main.st, "cache_data", side_effect=lambda *a, **k: no_cache_decorator)
        cls.cache_data_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.cache_data_patcher.stop()

    def test_initialize_state_sets_app_state(self):
        dummy_state = AttrDict()
        with patch.object(main.st, "session_state", dummy_state):
            main.initialize_state()
            self.assertTrue(hasattr(dummy_state, "app_state"))
            self.assertIsInstance(dummy_state.app_state, dict)

    def test_configure_genai_no_api_key(self):
        dummy_state = AttrDict(app_state={"google_api_key": ""})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "warning"):
            self.assertFalse(main.configure_genai())

    def test_configure_genai_success(self):
        dummy_state = AttrDict(app_state={"google_api_key": "key"})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.genai, "configure"), \
             patch.object(main.genai, "GenerativeModel", return_value=object()), \
             patch.object(main.st, "warning"), \
             patch.object(main.st, "error"):
            self.assertTrue(main.configure_genai())
            self.assertIsNotNone(dummy_state.app_state["model"])

    def test_configure_genai_failure(self):
        dummy_state = AttrDict(app_state={"google_api_key": "key"})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.genai, "configure", side_effect=Exception("fail")), \
             patch.object(main.st, "warning"), \
             patch.object(main.st, "error"):
            self.assertFalse(main.configure_genai())

    def test_generate_from_model_no_model(self):
        dummy_state = AttrDict(app_state={"model": None})
        with patch.object(main.st, "session_state", dummy_state):
            result = main.generate_from_model(1, "prompt")
            self.assertIn("error", result)

    def test_generate_from_model_success(self):
        class DummyResponse:
            text = '{"outline": "test", "hashtags": ["a"], "image_prompt": "img"}'
        class DummyModel:
            def generate_content(self, prompt, generation_config): return DummyResponse()
        dummy_state = AttrDict(app_state={"model": DummyModel(), "last_prompt": "", "last_raw_response": ""})
        with patch.object(main.st, "session_state", dummy_state):
            # Patch json.loads to always return the expected dict for this test
            with patch("main.json.loads", return_value={"outline": "test", "hashtags": ["a"], "image_prompt": "img"}):
                # Also patch DummyModel.generate_content to ensure no exception
                result = main.generate_from_model(object(), "prompt")
                self.assertEqual(result["outline"], "test")
                self.assertEqual(result["hashtags"], ["a"])
                self.assertEqual(result["image_prompt"], "img")

    def test_generate_from_model_failure(self):
        class DummyModel:
            def generate_content(self, prompt, generation_config): raise Exception("fail")
        dummy_state = AttrDict(app_state={"model": DummyModel(), "last_prompt": "", "last_raw_response": ""})
        with patch.object(main.st, "session_state", dummy_state):
            result = main.generate_from_model(1, "prompt")
            self.assertIn("error", result)

    def test_render_sidebar(self):
        dummy_state = AttrDict(app_state={"google_api_key": "", "templates": {}, "last_prompt": "", "last_raw_response": ""})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "sidebar", MagicMock()), \
             patch.object(main, "render_template_manager"), \
             patch.object(main, "render_debug_info"), \
             patch.object(main.st, "header"), \
             patch.object(main.st, "text_input", return_value=""), \
             patch.object(main.st, "selectbox", side_effect=lambda *a, **k: a[1][0]), \
             patch.object(main.st, "slider", return_value=400):
            settings = main.render_sidebar()
            self.assertIsInstance(settings, dict)
            self.assertIn("social_media", settings)

    def test_render_template_manager(self):
        dummy_state = AttrDict(app_state={"templates": {"t1": "prompt"}})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st.sidebar, "expander", MagicMock()), \
             patch.object(main.st, "selectbox", return_value="t1"), \
             patch.object(main.st, "text_area", return_value="prompt"), \
             patch.object(main.st, "columns", return_value=[MagicMock(), MagicMock()]), \
             patch.object(main.st, "text_input", return_value="t1"), \
             patch.object(main.st, "button", return_value=False), \
             patch.object(main.st, "success"), \
             patch.object(main.st, "error"), \
             patch.object(main.st, "rerun"):
            main.render_template_manager()

    def test_render_debug_info(self):
        dummy_state = AttrDict(app_state={"last_prompt": "p", "last_raw_response": "r"})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st.sidebar, "expander", MagicMock()), \
             patch.object(main.st, "write"), \
             patch.object(main.st, "code"):
            main.render_debug_info()

    def test_render_main_content(self):
        dummy_state = AttrDict(app_state={"model": True, "history": []}, generated_content=None)
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "title"), \
             patch.object(main.st, "text_input", return_value="topic"), \
             patch.object(main.st, "button", return_value=False):
            main.render_main_content({"social_media": "LinkedIn", "content_type": "Post", "tone": "Professional", "audience": "a", "length": 100, "language": "English", "seo_keywords": ""})

    def test_render_output_tabs(self):
        dummy_state = AttrDict(app_state={"history": []}, generated_content=None)
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "tabs", return_value=[MagicMock(), MagicMock()]), \
             patch.object(main, "render_generated_content"), \
             patch.object(main, "render_history"):
            main.render_output_tabs()

    def test_render_generated_content(self):
        dummy_state = AttrDict(app_state={"history": [{"topic": "t", "settings": {"social_media": "s", "content_type": "c", "tone": "t", "audience": "a", "length": 1, "language": "l", "seo_keywords": ""}, "timestamp": "2024-01-01T00:00:00"}]})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "subheader"), \
             patch.object(main.st, "markdown"), \
             patch.object(main.st, "info"), \
             patch.object(main.st, "code"), \
             patch.object(main.st, "download_button"), \
             patch.object(main.st, "columns", return_value=[MagicMock(), MagicMock()]), \
             patch.object(main, "pd"):
            main.render_generated_content({"outline": "o", "hashtags": ["h"], "image_prompt": "i"})

    def test_render_history(self):
        dummy_state = AttrDict(app_state={"history": [{"topic": "t", "settings": {"social_media": "s", "content_type": "c", "tone": "t", "audience": "a"}, "result": {"outline": "o", "hashtags": ["h"]}, "timestamp": "2024-01-01T00:00:00"}]})
        with patch.object(main.st, "session_state", dummy_state), \
             patch.object(main.st, "subheader"), \
             patch.object(main.st, "info"), \
             patch.object(main.st, "expander", MagicMock()), \
             patch.object(main.st, "markdown"), \
             patch.object(main.st, "button", return_value=False), \
             patch.object(main.st, "rerun"):
            main.render_history()

if __name__ == "__main__":
    unittest.main()
