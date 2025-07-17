#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Performance tests for Academic Submission System.

Tests validation speed, memory usage, and scalability.
"""

import concurrent.futures
import os
import time

import psutil
import pytest
from quality_assurance.submission_validator import SubmissionValidator


class TestValidationPerformance:
    """Performance tests for validation operations."""

    @pytest.mark.performance
    def test_single_paper_validation_speed(self, complete_paper):
        """Test validation speed for a single paper."""
        start_time = time.time()

        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()

        end_time = time.time()
        validation_time = end_time - start_time

        # Validation should complete within reasonable time
        assert (
            validation_time < 10.0
        ), f"Validation took {validation_time:.2f}s, expected < 10s"
        assert report.overall_status is not None

        print(f"Single paper validation: {validation_time:.2f}s")

    @pytest.mark.performance
    def test_minimal_paper_validation_speed(self, minimal_paper):
        """Test validation speed for minimal paper."""
        start_time = time.time()

        validator = SubmissionValidator(str(minimal_paper))
        report = validator.validate_submission()

        end_time = time.time()
        validation_time = end_time - start_time

        # Minimal paper should validate very quickly
        assert (
            validation_time < 5.0
        ), f"Minimal validation took {validation_time:.2f}s, expected < 5s"
        assert report.overall_status is not None

        print(f"Minimal paper validation: {validation_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_paper_validation_speed(self, performance_paper):
        """Test validation speed for large paper."""
        start_time = time.time()

        validator = SubmissionValidator(str(performance_paper))
        report = validator.validate_submission()

        end_time = time.time()
        validation_time = end_time - start_time

        # Large paper should still validate within reasonable time
        assert (
            validation_time < 30.0
        ), f"Large validation took {validation_time:.2f}s, expected < 30s"
        assert report.overall_status is not None

        print(f"Large paper validation: {validation_time:.2f}s")

    @pytest.mark.performance
    def test_memory_usage_single_validation(self, complete_paper):
        """Test memory usage during single validation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()

        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable
        assert (
            memory_increase < 50
        ), f"Memory increased by {memory_increase:.1f}MB, expected < 50MB"
        assert report.overall_status is not None

        print(
            f"Memory usage: {initial_memory:.1f}MB -> {peak_memory:.1f}MB"
            f" (+{memory_increase:.1f}MB)"
        )

    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_multiple_validations(self, complete_paper):
        """Test memory usage during multiple validations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run multiple validations
        for i in range(10):
            validator = SubmissionValidator(str(complete_paper))
            report = validator.validate_submission()
            assert report.overall_status is not None

            # Clean up references
            del validator, report

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be bounded (no major leaks)
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase:.1f}MB after 10 validations"

        print(
            f"Memory after 10 validations: {initial_memory:.1f}MB ->"
            f" {final_memory:.1f}MB (+{memory_increase:.1f}MB)"
        )

    @pytest.mark.performance
    def test_concurrent_validation_performance(self, complete_paper, minimal_paper):
        """Test performance of concurrent validations."""
        papers = [complete_paper, minimal_paper] * 3  # 6 papers total
        num_workers = 3

        def validate_paper(paper_path):
            start_time = time.time()
            validator = SubmissionValidator(str(paper_path))
            report = validator.validate_submission()
            end_time = time.time()
            return report, end_time - start_time

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(validate_paper, paper) for paper in papers]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        total_time = time.time() - start_time

        # All validations should complete
        assert len(results) == len(papers)
        for report, validation_time in results:
            assert report.overall_status is not None
            assert validation_time < 15.0  # Individual validation time

        # Concurrent execution should be faster than sequential
        avg_time = sum(validation_time for _, validation_time in results) / len(results)
        efficiency = avg_time * len(papers) / total_time

        assert (
            total_time < 60.0
        ), f"Concurrent validation took {total_time:.2f}s, expected < 60s"
        assert (
            efficiency > 1.5
        ), f"Concurrency efficiency {efficiency:.2f}, expected > 1.5x"

        print(
            f"Concurrent validation: {total_time:.2f}s total, {avg_time:.2f}s average,"
            f" {efficiency:.2f}x efficiency"
        )

    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_validation_benchmark(self, benchmark, complete_paper):
        """Benchmark validation performance using pytest-benchmark."""

        def run_validation():
            validator = SubmissionValidator(str(complete_paper))
            return validator.validate_submission()

        # Run benchmark
        result = benchmark(run_validation)

        # Verify result
        assert result.overall_status is not None
        assert len(result.validation_results) > 0

    @pytest.mark.performance
    def test_file_io_performance(self, temp_dir):
        """Test file I/O performance with various file sizes."""
        # Create papers of different sizes
        sizes = [1, 10, 100]  # KB
        validation_times = []

        for size_kb in sizes:
            paper_dir = temp_dir / f"paper_{size_kb}kb"
            paper_dir.mkdir()

            # Create content of specified size
            content_size = size_kb * 1024  # bytes
            content = "Test content. " * (content_size // 13)  # Approximate size

            (paper_dir / "main.tex").write_text(
                f"""
\\documentclass{{article}}
\\begin{{document}}
\\title{{Test Paper {size_kb}KB}}
\\author{{Test Author}}
\\begin{{abstract}}
Test abstract.
\\end{{abstract}}
\\section{{Content}}
{content}
\\end{{document}}
"""
            )

            (paper_dir / "README.txt").write_text(f"Test paper {size_kb}KB")

            # Measure validation time
            start_time = time.time()
            validator = SubmissionValidator(str(paper_dir))
            report = validator.validate_submission()
            validation_time = time.time() - start_time

            validation_times.append(validation_time)
            assert report.overall_status is not None

            print(f"Paper {size_kb}KB: {validation_time:.3f}s")

        # Validation time should scale reasonably with file size
        # Larger files shouldn't be dramatically slower for simple content
        assert all(t < 10.0 for t in validation_times), "Some validations too slow"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_stress_validation(self, minimal_paper):
        """Stress test with many rapid validations."""
        num_validations = 50
        start_time = time.time()

        for i in range(num_validations):
            validator = SubmissionValidator(str(minimal_paper))
            report = validator.validate_submission()
            assert report.overall_status is not None

            # Clean up
            del validator, report

        total_time = time.time() - start_time
        avg_time = total_time / num_validations

        # Should handle rapid validations efficiently
        assert (
            total_time < 120.0
        ), f"Stress test took {total_time:.2f}s for {num_validations} validations"
        assert avg_time < 3.0, f"Average validation time {avg_time:.3f}s, expected < 3s"

        print(
            f"Stress test: {num_validations} validations in {total_time:.2f}s (avg:"
            f" {avg_time:.3f}s)"
        )


class TestScalabilityPerformance:
    """Scalability performance tests."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_bibliography_size_scaling(self, temp_dir):
        """Test performance scaling with bibliography size."""
        bib_sizes = [10, 50, 100, 200]
        validation_times = []

        for num_refs in bib_sizes:
            paper_dir = temp_dir / f"paper_refs_{num_refs}"
            paper_dir.mkdir()

            # Create main.tex
            (paper_dir / "main.tex").write_text(
                """
\\documentclass{article}
\\begin{document}
\\title{Bibliography Scaling Test}
\\author{Test Author}
\\begin{abstract}
Test abstract.
\\end{abstract}
\\section{Introduction}
Test content.
\\end{document}
"""
            )

            # Create large bibliography
            bib_entries = []
            for i in range(num_refs):
                bib_entries.append(
                    f"""
@article{{ref{i:04d},
    title={{Reference {i}: A Comprehensive Study}},
    author={{Author {i}, First and Author {i}, Second}},
    journal={{Journal of Reference {i % 10}}},
    volume={{{i % 50 + 1}}},
    number={{{i % 12 + 1}}},
    pages={{{i * 10}--{i * 10 + 15}}},
    year={{2023}},
    doi={{10.1000/ref.{i:04d}}}
}}"""
                )

            (paper_dir / "references.bib").write_text("\n".join(bib_entries))
            (paper_dir / "README.txt").write_text(
                f"Test paper with {num_refs} references"
            )

            # Measure validation time
            start_time = time.time()
            validator = SubmissionValidator(str(paper_dir))
            report = validator.validate_submission()
            validation_time = time.time() - start_time

            validation_times.append(validation_time)
            assert report.overall_status is not None

            # Check bibliography validation
            bib_results = [
                r for r in report.validation_results if r.check_name == "Bibliography"
            ]
            assert len(bib_results) == 1
            assert f"{num_refs} entries" in bib_results[0].message

            print(f"Bibliography {num_refs} refs: {validation_time:.3f}s")

        # Validation time should scale sub-linearly with bibliography size
        # (O(n) or better, not O(n²))
        max_time = max(validation_times)
        assert (
            max_time < 15.0
        ), f"Large bibliography validation took {max_time:.2f}s, expected < 15s"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_figure_count_scaling(self, temp_dir):
        """Test performance scaling with number of figures."""
        figure_counts = [5, 15, 30]
        validation_times = []

        for num_figures in figure_counts:
            paper_dir = temp_dir / f"paper_figs_{num_figures}"
            paper_dir.mkdir()

            # Create figures directory
            figs_dir = paper_dir / "figs"
            figs_dir.mkdir()

            # Create figure files and references
            figure_refs = []
            for i in range(num_figures):
                fig_file = figs_dir / f"figure_{i:03d}.png"
                fig_file.write_bytes(b"fake_png_data")
                figure_refs.append(f"\\includegraphics{{figs/figure_{i:03d}.png}}")

            # Create main.tex with figure references
            (paper_dir / "main.tex").write_text(
                f"""
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\begin{{document}}
\\title{{Figure Scaling Test}}
\\author{{Test Author}}
\\begin{{abstract}}
Test abstract with {num_figures} figures.
\\end{{abstract}}
\\section{{Figures}}
{chr(10).join(figure_refs)}
\\end{{document}}
"""
            )

            (paper_dir / "README.txt").write_text(
                f"Test paper with {num_figures} figures"
            )

            # Measure validation time
            start_time = time.time()
            validator = SubmissionValidator(str(paper_dir))
            report = validator.validate_submission()
            validation_time = time.time() - start_time

            validation_times.append(validation_time)
            assert report.overall_status is not None

            # Check figure validation
            fig_results = [
                r for r in report.validation_results if r.check_name == "Figures"
            ]
            assert len(fig_results) == 1
            assert fig_results[0].status == "PASS"

            print(f"Figures {num_figures} count: {validation_time:.3f}s")

        # Should handle reasonable numbers of figures efficiently
        max_time = max(validation_times)
        assert (
            max_time < 10.0
        ), f"Many figures validation took {max_time:.2f}s, expected < 10s"


class TestResourceUsage:
    """Resource usage and efficiency tests."""

    @pytest.mark.performance
    def test_cpu_usage_efficiency(self, complete_paper):
        """Test CPU usage during validation."""
        import threading

        cpu_percentages = []
        monitoring = True

        def monitor_cpu():
            while monitoring:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_percentages.append(cpu_percent)

        # Start CPU monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        try:
            # Run validation
            validator = SubmissionValidator(str(complete_paper))
            report = validator.validate_submission()
            assert report.overall_status is not None
        finally:
            monitoring = False
            monitor_thread.join()

        if cpu_percentages:
            avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
            max_cpu = max(cpu_percentages)

            # CPU usage should be reasonable
            assert max_cpu < 90.0, f"Peak CPU usage {max_cpu:.1f}%, expected < 90%"

            print(f"CPU usage: avg {avg_cpu:.1f}%, peak {max_cpu:.1f}%")

    @pytest.mark.performance
    def test_disk_io_efficiency(self, complete_paper):
        """Test disk I/O efficiency during validation."""
        process = psutil.Process(os.getpid())

        # Get initial I/O counters
        try:
            initial_io = process.io_counters()
            initial_read = initial_io.read_bytes
            initial_write = initial_io.write_bytes
        except AttributeError:
            pytest.skip("I/O counters not available on this platform")

        # Run validation
        validator = SubmissionValidator(str(complete_paper))
        report = validator.validate_submission()
        assert report.overall_status is not None

        # Get final I/O counters
        final_io = process.io_counters()
        read_bytes = final_io.read_bytes - initial_read
        write_bytes = final_io.write_bytes - initial_write

        # I/O should be reasonable for the operation
        read_mb = read_bytes / 1024 / 1024
        write_mb = write_bytes / 1024 / 1024

        assert read_mb < 10.0, f"Read {read_mb:.2f}MB, expected < 10MB"
        assert write_mb < 5.0, f"Wrote {write_mb:.2f}MB, expected < 5MB"

        print(f"Disk I/O: read {read_mb:.2f}MB, write {write_mb:.2f}MB")
