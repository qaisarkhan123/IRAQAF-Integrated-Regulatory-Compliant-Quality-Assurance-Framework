# Code Quality Recommendations

## ✅ Completed Improvements

1. **Import Organization** - Organized by: stdlib → third-party → local
2. **Removed Duplicates** - Eliminated duplicate function definitions
3. **Type Hints** - Modernized to Python 3.10+ syntax
4. **Documentation** - Added docstrings to utility functions
5. **Bug Fixes** - Fixed undefined variable references

---

## 🎯 Additional Recommendations (Optional Future Improvements)

### 1. **Extract Long Functions into Smaller Units**
   - **Current Issue:** Some functions are quite large (100+ lines)
   - **Benefit:** Easier to test, debug, and maintain
   - **Example:** The `_fit_and_measure()` function could be split into:
     - `_prepare_data()` - data loading & preprocessing
     - `_train_model()` - model training
     - `_evaluate_model()` - metrics calculation

### 2. **Create Constants File**
   - **Current Issue:** Magic numbers and strings scattered throughout (e.g., "50MB", file extensions)
   - **Benefit:** Easy to update values globally
   - **Example:** Create `constants.py` with:
     ```python
     MAX_FILE_SIZE = 50 * 1024 * 1024
     ALLOWED_EXTENSIONS = {'.pdf', '.csv', '.txt', ...}
     SEED = 42
     ```

### 3. **Add Type Hints to All Functions**
   - **Current Status:** ~80% of functions have type hints
   - **Recommendation:** Add to remaining functions
   - **Example:**
     ```python
     # Before
     def _as_dict_list(obj):
     
     # After
     def _as_dict_list(obj: Any) -> list[dict]:
     ```

### 4. **Implement Logging Levels Consistently**
   - Use `logger.debug()` for development-only info
   - Use `logger.info()` for important operational events
   - Use `logger.warning()` for recoverable issues
   - Use `logger.error()` for critical failures

### 5. **Add Input Validation**
   - Most functions accept `path` parameters without validation
   - Consider wrapping with decorators:
     ```python
     def validate_path(func):
         def wrapper(path, *args, **kwargs):
             if not Path(path).exists():
                 raise FileNotFoundError(f"Path not found: {path}")
             return func(path, *args, **kwargs)
         return wrapper
     ```

### 6. **Extract Streamlit UI Components**
   - Group UI-related functions into separate `ui_components.py`
   - Benefits:
     - Reusable across pages
     - Easier to test (using mocks)
     - Clearer separation of concerns

### 7. **Add Comprehensive Docstrings (Google Style)**
   ```python
   # Current
   def card(title: str, subtitle: str | None = None):
       """Render opening HTML for a styled card container."""
   
   # Recommended
   def card(title: str, subtitle: str | None = None):
       """Render opening HTML for a styled card container.
       
       Args:
           title: Main card title text
           subtitle: Optional secondary text
           
       Returns:
           None (renders directly to Streamlit)
           
       Example:
           >>> card("Dashboard", "Real-time Analytics")
           >>> # Card HTML is rendered
           >>> close_card()
       """
   ```

### 8. **Error Handling Improvements**
   - Current: Generic try-except blocks
   - Recommended: Specific exception handling
   ```python
   # Before
   except Exception as e:
       logger.error(f"Failed: {e}")
   
   # After
   except FileNotFoundError:
       logger.error(f"File not found: {path}")
   except json.JSONDecodeError as e:
       logger.error(f"Invalid JSON at line {e.lineno}: {e.msg}")
   except Exception as e:
       logger.error(f"Unexpected error: {e}", exc_info=True)
   ```

### 9. **Add Configuration Management**
   - Move hardcoded paths to config file
   - Use environment variables for sensitive data
   - Example structure:
     ```yaml
     paths:
       evidence_index: "configs/evidence_index.json"
       policies: "configs/policies.yaml"
       incidents: "data/incidents.json"
     
     limits:
       max_file_size_mb: 50
       max_history: 20
     ```

### 10. **Create Unit Tests**
   - Functions like `_as_dict_list()`, `validate_and_sanitize_input()` are good candidates
   - Example test structure:
     ```python
     import pytest
     
     def test_as_dict_list_with_dict():
         result = _as_dict_list({"key": "value"})
         assert result == [{"key": "value"}]
     
     def test_as_dict_list_with_list():
         result = _as_dict_list([{"a": 1}, {"b": 2}])
         assert result == [{"a": 1}, {"b": 2}]
     ```

---

## 🔍 Code Quality Metrics

| Aspect | Current | Target | Priority |
|--------|---------|--------|----------|
| Type hint coverage | ~80% | 100% | Medium |
| Docstring coverage | ~70% | 100% | Medium |
| Function size | 50-150 lines avg | <50 lines | Low |
| Test coverage | ~0% | 80%+ | High |
| Error handling specificity | Generic | Specific | Medium |

---

## 📋 Quick Checklist for Next Steps

- [ ] Review and address import-related issues (missing packages)
- [ ] Add type hints to remaining functions
- [ ] Expand docstrings with Args/Returns/Examples
- [ ] Create `constants.py` for magic numbers
- [ ] Add basic unit tests for utility functions
- [ ] Create configuration YAML file
- [ ] Implement environment-based settings
- [ ] Extract reusable UI components
- [ ] Add specific exception handling
- [ ] Document public API with comprehensive examples

---

## 🎓 Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Docstring Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints in Python](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Your code is now well-structured and ready for these enhancements!** 🚀
