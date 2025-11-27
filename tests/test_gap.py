"""Tests for the GAP wrapper class.

These tests require GAP (Groups, Algorithms, Programming) to be installed 
and available in the system PATH.
"""

import pytest
from unittest.mock import Mock, patch


class TestGAPInitialization:
    """Tests for GAP class initialization."""

    def test_init_creates_process(self):
        """Test that initialization creates a GAP process."""
        from gapwrapper import GAP
        gap = GAP()
        try:
            assert gap.process is not None
            assert gap.process.poll() is None  # Process is running
        finally:
            gap.close()

    def test_init_with_default_executable(self):
        """Test initialization with default executable."""
        from gapwrapper import GAP
        gap = GAP()
        try:
            # Should be able to execute a simple command
            result = gap("1+1;")
            assert "2" in result
        finally:
            gap.close()


class TestGAPCommandExecution:
    """Tests for GAP command execution."""

    @pytest.fixture
    def gap(self):
        """Create a GAP instance for testing."""
        from gapwrapper import GAP
        gap = GAP()
        yield gap
        gap.close()

    def test_simple_arithmetic(self, gap):
        """Test simple arithmetic operations."""
        result = gap("1 + 1;")
        assert "2" in result

    def test_multiplication(self, gap):
        """Test multiplication."""
        result = gap("6 * 7;")
        assert "42" in result

    def test_factorial(self, gap):
        """Test factorial function."""
        result = gap("Factorial(5);")
        assert "120" in result

    def test_adds_semicolon_if_missing(self, gap):
        """Test that __call__ adds semicolon if command doesn't end with one."""
        result = gap("2 + 3")
        assert "5" in result

    def test_preserves_existing_semicolon(self, gap):
        """Test that __call__ preserves existing semicolon."""
        result = gap("4 + 4;")
        assert "8" in result

    def test_multiline_output(self, gap):
        """Test commands that produce multiline output."""
        result = gap("Elements(SymmetricGroup(3));")
        # Should contain permutation elements
        assert "(" in result or "[" in result

    def test_define_variable(self, gap):
        """Test defining and using a variable."""
        gap("x := 10;")
        result = gap("x * 2;")
        assert "20" in result

    def test_define_group(self, gap):
        """Test defining a symmetric group."""
        result = gap("G := SymmetricGroup(4);")
        assert "Sym" in result or "SymmetricGroup" in result or "Group" in result

    def test_group_size(self, gap):
        """Test computing group size."""
        gap("G := SymmetricGroup(4);")
        result = gap("Size(G);")
        assert "24" in result

    def test_list_operations(self, gap):
        """Test list operations."""
        result = gap("[1,2,3,4,5];")
        assert "1" in result and "5" in result

    def test_list_sum(self, gap):
        """Test sum of a list."""
        result = gap("Sum([1,2,3,4,5]);")
        assert "15" in result

    def test_string_output(self, gap):
        """Test string output."""
        result = gap('Print("Hello");')
        assert "Hello" in result

    def test_boolean_true(self, gap):
        """Test boolean true."""
        result = gap("1 < 2;")
        assert "true" in result.lower()

    def test_boolean_false(self, gap):
        """Test boolean false."""
        result = gap("2 < 1;")
        assert "false" in result.lower()


class TestGAPOperators:
    """Tests for GAP operator overloading."""

    @pytest.fixture
    def gap(self):
        """Create a GAP instance for testing."""
        from gapwrapper import GAP
        gap = GAP()
        yield gap
        gap.close()

    def test_rshift_operator(self, gap):
        """Test that >> operator works like __call__."""
        result = gap >> "3 + 5;"
        assert "8" in result

    def test_rshift_chain(self, gap):
        """Test chaining >> operators."""
        gap >> "y := 100;"
        result = gap >> "y / 4;"
        assert "25" in result


class TestGAPContextManager:
    """Tests for GAP context manager functionality."""

    def test_context_manager_enter(self):
        """Test that __enter__ returns the GAP instance."""
        from gapwrapper import GAP
        with GAP() as gap:
            assert gap is not None
            assert hasattr(gap, 'process')
            assert gap.process.poll() is None  # Process is running

    def test_context_manager_exit_closes(self):
        """Test that __exit__ closes the process."""
        from gapwrapper import GAP
        import time
        
        with GAP() as gap:
            process = gap.process
        
        # After exiting context, process should be terminated
        # Poll with timeout instead of fixed sleep
        timeout = 5.0
        start = time.time()
        while process.poll() is None and (time.time() - start) < timeout:
            time.sleep(0.1)
        assert process.poll() is not None

    def test_context_manager_usage(self):
        """Test using GAP within context manager."""
        from gapwrapper import GAP
        with GAP() as gap:
            result = gap("10 * 10;")
            assert "100" in result


class TestGAPClose:
    """Tests for GAP close functionality."""

    def test_close_terminates_process(self):
        """Test that close() terminates the process."""
        from gapwrapper import GAP
        import time
        
        gap = GAP()
        process = gap.process
        
        gap.close()
        
        # Process should be terminated
        # Poll with timeout instead of fixed sleep
        timeout = 5.0
        start = time.time()
        while process.poll() is None and (time.time() - start) < timeout:
            time.sleep(0.1)
        assert process.poll() is not None

    def test_close_is_idempotent(self):
        """Test that close() can be called multiple times safely."""
        from gapwrapper import GAP
        gap = GAP()
        
        # Should not raise any exception
        gap.close()
        gap.close()
        gap.close()


class TestGAPErrorHandling:
    """Tests for GAP error handling."""

    @pytest.fixture
    def gap(self):
        """Create a GAP instance for testing."""
        from gapwrapper import GAP
        gap = GAP()
        yield gap
        gap.close()

    def test_undefined_variable_handling(self, gap):
        """Test handling of undefined variables."""
        result = gap("UndefinedVariable12345;")
        # Should return some error message or indication
        assert result is not None

    def test_syntax_error_handling(self, gap):
        """Test handling of syntax errors."""
        result = gap("1 + + 1;")
        # Should return some error or indication
        assert result is not None

    def test_continues_after_error(self, gap):
        """Test that GAP continues working after an error."""
        # Cause an error
        gap("InvalidCommand12345;")
        
        # Should still be able to execute valid commands
        result = gap("1 + 1;")
        assert "2" in result


class TestGAPBrokenPipe:
    """Tests for broken pipe handling."""

    def test_broken_pipe_raises_runtime_error(self):
        """Test that broken pipe raises RuntimeError."""
        from gapwrapper import GAP
        gap = GAP()
        
        # Close the process to simulate broken pipe
        gap.process.terminate()
        gap.process.wait()
        
        with pytest.raises(RuntimeError, match="GAP process has terminated"):
            gap("1+1;")


class TestGAPModuleExports:
    """Tests for module exports."""

    def test_gap_exported_from_package(self):
        """Test that GAP class is exported from gapwrapper package."""
        from gapwrapper import GAP
        assert GAP is not None

    def test_all_contains_gap(self):
        """Test that __all__ contains 'GAP'."""
        import gapwrapper
        assert 'GAP' in gapwrapper.__all__

    def test_gap_class_has_expected_methods(self):
        """Test that GAP class has expected methods."""
        from gapwrapper import GAP
        assert hasattr(GAP, '__call__')
        assert hasattr(GAP, '__rshift__')
        assert hasattr(GAP, '__enter__')
        assert hasattr(GAP, '__exit__')
        assert hasattr(GAP, 'close')
