#!/usr/bin/env python
"""
PyBoy Emulator Benchmark Suite

A specialized benchmark tool for testing the PyBoy GameBoy emulator using
the BotSupport API. This benchmark suite is specifically designed for the
PyBoy emulator architecture.
"""

import os
import time
import json
import argparse
import statistics
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Any, Optional, Set

import pyboy
from pyboy import PyBoy


@dataclass
class BenchmarkResult:
    """Data class for storing benchmark results"""
    name: str
    description: str
    duration: float  # seconds
    frames_executed: int
    frames_per_second: float
    cpu_cycles: int
    cycles_per_second: float
    metrics: Dict[str, Any] = field(default_factory=dict)


class PyBoyBenchmark:
    """Base class for PyBoy emulator benchmarks"""

    def __init__(self, rom_path: str, headless: bool = True, **kwargs):
        """Initialize the benchmark with a ROM path"""
        self.rom_path = rom_path
        self.name = os.path.basename(rom_path)
        self.description = ""
        self.pyboy_instance = None
        self.headless = headless
        self.kwargs = kwargs
        self.duration = 0
        self.frames_executed = 0
        self.cpu_cycles_start = 0
        self.cpu_cycles_end = 0

    def setup(self) -> None:
        """Set up the benchmark environment"""
        # Initialize PyBoy with appropriate settings
        window_type = "headless" if self.headless else "SDL2"
        self.pyboy_instance = PyBoy(
            self.rom_path,
            window_type=window_type,
            **self.kwargs
        )
        self.pyboy_instance.set_emulation_speed(0)  # Run as fast as possible

        # Reset metrics
        self.duration = 0
        self.frames_executed = 0

        # Access bot support directly
        self.bot_support = self.pyboy_instance.botsupport_manager()
        self.cpu_cycles_start = self.bot_support.cpu().cycles

    def run(self, frames: int = 60) -> BenchmarkResult:
        """Run the benchmark for a specific number of frames"""
        if self.pyboy_instance is None:
            self.setup()

        # Start timing
        start_time = time.time()

        # Store initial CPU cycles
        self.cpu_cycles_start = self.bot_support.cpu().cycles

        # Run for specified number of frames
        for _ in range(frames):
            self.pyboy_instance.tick()

        # End timing
        end_time = time.time()
        self.duration = end_time - start_time
        self.frames_executed = frames

        # Get final CPU cycles
        self.cpu_cycles_end = self.bot_support.cpu().cycles

        # Calculate metrics
        cycles_executed = self.cpu_cycles_end - self.cpu_cycles_start

        result = BenchmarkResult(
            name=self.name,
            description=self.description,
            duration=self.duration,
            frames_executed=frames,
            frames_per_second=frames / self.duration,
            cpu_cycles=cycles_executed,
            cycles_per_second=cycles_executed / self.duration
        )

        # Add additional metrics from subclasses
        result.metrics.update(self.collect_metrics())

        return result

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect additional metrics for the benchmark - to be implemented by subclasses"""
        return {}

    def teardown(self) -> None:
        """Clean up resources"""
        if self.pyboy_instance:
            self.pyboy_instance.stop(save=False)
            self.pyboy_instance = None


class CPUBenchmark(PyBoyBenchmark):
    """Benchmark focused on CPU performance and instruction execution"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures CPU performance and instruction execution"
        self.instruction_counts = {}
        self.interrupt_counts = {
            "vblank": 0,
            "lcdc": 0,
            "timer": 0,
            "serial": 0,
            "hightolow": 0
        }

    def run(self, frames: int = 600) -> BenchmarkResult:
        """Run the CPU benchmark with instruction tracking"""
        if self.pyboy_instance is None:
            self.setup()

        # Start timing
        start_time = time.time()

        # Store initial CPU cycles
        self.cpu_cycles_start = self.bot_support.cpu().cycles

        # Run for specified number of frames
        for _ in range(frames):
            # Track interrupt register before frame
            interrupt_flag_before = self.pyboy_instance.get_memory_value(0xFF0F)

            self.pyboy_instance.tick()

            # Track interrupt register after frame
            interrupt_flag_after = self.pyboy_instance.get_memory_value(0xFF0F)

            # Check which interrupts occurred
            interrupt_diff = interrupt_flag_before ^ interrupt_flag_after
            if interrupt_diff & 0x01:  # VBLANK
                self.interrupt_counts["vblank"] += 1
            if interrupt_diff & 0x02:  # LCDC
                self.interrupt_counts["lcdc"] += 1
            if interrupt_diff & 0x04:  # TIMER
                self.interrupt_counts["timer"] += 1
            if interrupt_diff & 0x08:  # SERIAL
                self.interrupt_counts["serial"] += 1
            if interrupt_diff & 0x10:  # HIGH-TO-LOW
                self.interrupt_counts["hightolow"] += 1

        # End timing
        end_time = time.time()
        self.duration = end_time - start_time
        self.frames_executed = frames

        # Get final CPU cycles
        self.cpu_cycles_end = self.bot_support.cpu().cycles

        # Calculate result
        result = super().run(0)  # 0 because we've already executed the frames
        return result

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect CPU-specific metrics"""
        metrics = {}

        # Get CPU state
        cpu = self.bot_support.cpu()

        # CPU state metrics
        metrics["cpu_state"] = {
            "pc": cpu.pc,
            "sp": cpu.sp,
            "a": cpu.a,
            "b": cpu.b,
            "c": cpu.c,
            "d": cpu.d,
            "e": cpu.e,
            "h": cpu.h,
            "l": cpu.l,
            "ime": 1 if cpu.ime else 0,
            "interrupts_enabled": self.pyboy_instance.get_memory_value(0xFFFF),
            "interrupts_flag": self.pyboy_instance.get_memory_value(0xFF0F)
        }

        # Interrupt statistics
        metrics["interrupts"] = self.interrupt_counts

        # Memory access patterns (sample key addresses)
        ram = self.bot_support.ram()
        metrics["memory_samples"] = {
            "hram": [ram[addr] for addr in range(0xFF80, 0xFFFF, 8)],
            "vram": [ram[addr] for addr in range(0x8000, 0x9000, 64)],
            "wram": [ram[addr] for addr in range(0xC000, 0xD000, 64)]
        }

        # Instruction timing (estimated)
        avg_cycles_per_instruction = 4.0  # Approximate - actual varies by instruction
        metrics["instruction_estimates"] = {
            "estimated_instructions_executed": self.cpu_cycles_end // avg_cycles_per_instruction,
            "instructions_per_second": (self.cpu_cycles_end // avg_cycles_per_instruction) / self.duration,
            "avg_instructions_per_frame": (self.cpu_cycles_end // avg_cycles_per_instruction) / self.frames_executed
        }

        return metrics


class MemoryBenchmark(PyBoyBenchmark):
    """Benchmark focused on memory access patterns and performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures memory access and cartridge performance"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect memory-specific metrics"""
        metrics = {}

        # Get cartridge info
        mb = self.pyboy_instance.mb
        metrics["cartridge"] = {
            "type": str(mb.cartridge),
            "rom_size": mb.cartridge.rom_size,
            "ram_size": mb.cartridge.ram_size,
            "cgb": mb.cartridge.cgb,
            "mbc": mb.cartridge.mbc,
            "rom_banks": mb.cartridge.external_rom_count,
            "ram_banks": mb.cartridge.external_ram_count
        }

        # Memory bank states
        metrics["memory_banks"] = {
            "rom_bank_selected": mb.cartridge.rombank_selected,
            "ram_bank_selected": mb.cartridge.rambank_selected
        }

        # Memory region statistics
        ram = self.bot_support.ram()

        # Sample different memory regions
        regions = {
            "rom_bank0": (0x0000, 0x4000, 256),
            "rom_bankn": (0x4000, 0x8000, 256),
            "vram": (0x8000, 0xA000, 128),
            "extram": (0xA000, 0xC000, 128),
            "wram": (0xC000, 0xE000, 128),
            "oam": (0xFE00, 0xFEA0, 32),
            "io": (0xFF00, 0xFF80, 16),
            "hram": (0xFF80, 0xFFFF, 16)
        }

        memory_stats = {}
        for region_name, (start, end, sample_count) in regions.items():
            # Take evenly spaced samples
            step = max(1, (end - start) // sample_count)
            samples = [ram[addr] for addr in range(start, end, step)]

            # Calculate statistics for this region
            region_stats = {
                "non_zero_ratio": sum(1 for s in samples if s != 0) / len(samples),
                "unique_values": len(set(samples)),
                "max_value": max(samples),
                "avg_value": sum(samples) / len(samples)
            }
            memory_stats[region_name] = region_stats

        metrics["memory_stats"] = memory_stats

        return metrics


class LCDBenchmark(PyBoyBenchmark):
    """Benchmark focused on LCD rendering and performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures LCD and graphics performance"
        self.frame_times = []
        self.lcd_stats = {
            "mode_0_time": 0,  # HBlank
            "mode_1_time": 0,  # VBlank
            "mode_2_time": 0,  # OAM scan
            "mode_3_time": 0,  # Pixel transfer
        }
        self.lcd_mode_transitions = 0

    def run(self, frames: int = 300) -> BenchmarkResult:
        """Run the LCD benchmark with detailed timing"""
        if self.pyboy_instance is None:
            self.setup()

        # Start timing
        start_time = time.time()

        # Store initial CPU cycles
        self.cpu_cycles_start = self.bot_support.cpu().cycles

        # Run for specified number of frames with per-frame timing
        self.frame_times = []

        for _ in range(frames):
            # Record LCD mode at start
            lcd_stat_before = self.pyboy_instance.get_memory_value(0xFF41)
            mode_before = lcd_stat_before & 0x3

            frame_start = time.time()
            self.pyboy_instance.tick()
            frame_end = time.time()

            # Record LCD mode at end
            lcd_stat_after = self.pyboy_instance.get_memory_value(0xFF41)
            mode_after = lcd_stat_after & 0x3

            # Track mode transition (simplified - full tracking would require more granular access)
            if mode_before != mode_after:
                self.lcd_mode_transitions += 1

            self.frame_times.append(frame_end - frame_start)

        # End timing
        end_time = time.time()
        self.duration = end_time - start_time
        self.frames_executed = frames

        # Get final CPU cycles
        self.cpu_cycles_end = self.bot_support.cpu().cycles

        # Calculate result
        result = super().run(0)  # 0 because we've already executed the frames
        return result

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect LCD-specific metrics"""
        metrics = {}

        # Get LCD state
        screen = self.bot_support.screen()

        # Frame time statistics
        if self.frame_times:
            metrics["frame_time_stats"] = {
                "min_ms": min(self.frame_times) * 1000,
                "max_ms": max(self.frame_times) * 1000,
                "avg_ms": statistics.mean(self.frame_times) * 1000,
                "median_ms": statistics.median(self.frame_times) * 1000,
                "stdev_ms": statistics.stdev(self.frame_times) * 1000 if len(self.frame_times) > 1 else 0
            }

        # LCD register state
        ram = self.bot_support.ram()
        metrics["lcd_registers"] = {
            "lcdc": ram[0xFF40],
            "stat": ram[0xFF41],
            "scy": ram[0xFF42],
            "scx": ram[0xFF43],
            "ly": ram[0xFF44],
            "lyc": ram[0xFF45],
            "bgp": ram[0xFF47],
            "obp0": ram[0xFF48],
            "obp1": ram[0xFF49],
            "wy": ram[0xFF4A],
            "wx": ram[0xFF4B]
        }

        # Sprite data
        sprites = screen.sprite_list()
        metrics["sprites"] = {
            "count": len(sprites),
            "visible_count": sum(1 for s in sprites if 0 <= s.x <= 160 and 0 <= s.y <= 144)
        }

        # Tile data
        used_tiles = set()
        for y in range(0, 32):
            for x in range(0, 32):
                tile_idx = screen.tilemap_position_list()[y * 32 + x]
                used_tiles.add(tile_idx)

        metrics["tiles"] = {
            "unique_tiles_used": len(used_tiles),
            "tile_cache_size": sum(1 for t in range(384) if screen.tile_cache_valid(t))
        }

        # LCD Mode statistics
        metrics["lcd_modes"] = {
            "mode_transitions": self.lcd_mode_transitions,
            "estimated_transitions_per_frame": self.lcd_mode_transitions / self.frames_executed
        }

        return metrics


class TimerBenchmark(PyBoyBenchmark):
    """Benchmark focused on timer accuracy and performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures timer accuracy and performance"
        self.timer_values = []
        self.timer_periods = []

    def run(self, frames: int = 120) -> BenchmarkResult:
        """Run the timer benchmark with detailed timing"""
        if self.pyboy_instance is None:
            self.setup()

        # Start timing
        start_time = time.time()

        # Store initial CPU cycles
        self.cpu_cycles_start = self.bot_support.cpu().cycles

        # Run for specified number of frames, capturing timer values
        self.timer_values = []
        last_div = None

        for _ in range(frames):
            # Record timer values before frame
            div_before = self.pyboy_instance.get_memory_value(0xFF04)
            tima_before = self.pyboy_instance.get_memory_value(0xFF05)

            self.pyboy_instance.tick()

            # Record timer values after frame
            div_after = self.pyboy_instance.get_memory_value(0xFF04)
            tima_after = self.pyboy_instance.get_memory_value(0xFF05)

            # Track DIV changes
            if last_div is not None:
                div_period = (div_after - last_div) & 0xFF
                self.timer_periods.append(div_period)
            last_div = div_after

            # Record timer data
            self.timer_values.append({
                "div": div_after,
                "tima": tima_after,
                "div_delta": (div_after - div_before) & 0xFF,
                "tima_delta": (tima_after - tima_before) & 0xFF
            })

        # End timing
        end_time = time.time()
        self.duration = end_time - start_time
        self.frames_executed = frames

        # Get final CPU cycles
        self.cpu_cycles_end = self.bot_support.cpu().cycles

        # Calculate result
        result = super().run(0)  # 0 because we've already executed the frames
        return result

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect timer-specific metrics"""
        metrics = {}

        # Current timer state
        ram = self.bot_support.ram()
        metrics["timer_registers"] = {
            "div": ram[0xFF04],
            "tima": ram[0xFF05],
            "tma": ram[0xFF06],
            "tac": ram[0xFF07]
        }

        # Analyze DIV register changes
        if self.timer_values:
            div_deltas = [entry["div_delta"] for entry in self.timer_values]
            tima_deltas = [entry["tima_delta"] for entry in self.timer_values]

            metrics["div_stats"] = {
                "avg_change_per_frame": sum(div_deltas) / len(div_deltas),
                "max_change": max(div_deltas),
                "min_change": min(div_deltas),
                "zero_count": div_deltas.count(0)
            }

            metrics["tima_stats"] = {
                "avg_change_per_frame": sum(tima_deltas) / len(tima_deltas),
                "max_change": max(tima_deltas),
                "non_zero_frames": sum(1 for d in tima_deltas if d > 0),
                "overflow_count": sum(1 for i in range(1, len(self.timer_values))
                                      if self.timer_values[i]["tima"] < self.timer_values[i - 1]["tima"])
            }

        # Timer frequency analysis (simplified)
        cpu_cycles_per_frame = self.cpu_cycles_end / self.frames_executed
        metrics["timer_frequency"] = {
            "cpu_cycles_per_frame": cpu_cycles_per_frame,
            "estimated_div_frequency": cpu_cycles_per_frame / 64  # DIV increments every 64 cycles
        }

        return metrics


class SoundBenchmark(PyBoyBenchmark):
    """Benchmark focused on sound emulation performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures sound system performance"
        # Force sound emulation to be enabled
        kwargs["sound_emulated"] = True

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect sound-specific metrics"""
        metrics = {}

        # Current sound register state
        ram = self.bot_support.ram()

        # Sound registers
        sound_regs = {}
        for addr in range(0xFF10, 0xFF40):
            sound_regs[f"0x{addr:04X}"] = ram[addr]

        metrics["sound_registers"] = sound_regs

        # Channel status (based on NR52 - 0xFF26)
        nr52 = ram[0xFF26]
        metrics["channel_status"] = {
            "channel1_on": bool(nr52 & 0x01),
            "channel2_on": bool(nr52 & 0x02),
            "channel3_on": bool(nr52 & 0x04),
            "channel4_on": bool(nr52 & 0x08),
            "sound_enabled": bool(nr52 & 0x80)
        }

        # Sound performance metrics (estimated)
        metrics["sound_performance"] = {
            "estimated_cpu_overhead": self.cpu_cycles_end * 0.05  # Rough estimate - 5% of CPU time
        }

        return metrics


class CartridgeBenchmark(PyBoyBenchmark):
    """Benchmark focused on cartridge access and MBC performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures cartridge access and MBC performance"

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect cartridge-specific metrics"""
        metrics = {}

        # Get direct access to cartridge
        mb = self.pyboy_instance.mb
        cart = mb.cartridge

        # Cartridge type information
        metrics["cartridge_type"] = {
            "type": str(cart),
            "mbc_type": cart.mbc,
            "rom_size": cart.rom_size,
            "ram_size": cart.ram_size,
            "rom_banks": cart.external_rom_count,
            "ram_banks": cart.external_ram_count,
            "battery": cart.battery,
            "rtc": cart.rtc,
            "rumble": cart.rumble
        }

        # Bank selection stats
        metrics["bank_state"] = {
            "rom_bank_selected": cart.rombank_selected,
            "ram_bank_selected": cart.rambank_selected,
            "rom_bank_selected_low": cart.rombank_selected_low,
            "ram_enabled": cart.ram_enabled
        }

        # Memory access patterns
        ram = self.bot_support.ram()

        # Sample ROM accesses (bank 0 and switchable)
        rom_samples = {
            "bank0": [ram[addr] for addr in range(0x0100, 0x4000, 256)],  # ROM bank 0
            "bankN": [ram[addr] for addr in range(0x4000, 0x8000, 256)]  # ROM bank N
        }

        # Analyze ROM access patterns
        rom_stats = {}
        for bank, samples in rom_samples.items():
            non_zero = sum(1 for s in samples if s != 0)
            rom_stats[bank] = {
                "non_zero_ratio": non_zero / len(samples),
                "unique_values": len(set(samples))
            }

        metrics["rom_access"] = rom_stats

        # RAM accesses (if available)
        if cart.ram_size > 0:
            ram_samples = [ram[addr] for addr in range(0xA000, 0xC000, 64)]
            metrics["external_ram"] = {
                "non_zero_ratio": sum(1 for s in ram_samples if s != 0) / len(ram_samples),
                "unique_values": len(set(ram_samples))
            }

        return metrics


class BotSupportBenchmark(PyBoyBenchmark):
    """Benchmark specifically for BotSupport API performance"""

    def __init__(self, rom_path: str, **kwargs):
        super().__init__(rom_path, **kwargs)
        self.description = "Measures BotSupport API performance"
        self.api_call_times = {
            "screen": [],
            "tilemap_background": [],
            "sprite_list": [],
            "set_pixel": []
        }

    def run(self, frames: int = 60) -> BenchmarkResult:
        """Run the BotSupport API benchmark"""
        if self.pyboy_instance is None:
            self.setup()

        # Start timing
        start_time = time.time()

        # Store initial CPU cycles
        self.cpu_cycles_start = self.bot_support.cpu().cycles

        # Run for specified number of frames, testing API performance
        for _ in range(frames):
            # Execute frame
            self.pyboy_instance.tick()

            # Benchmark screen access
            t_start = time.time()
            screen = self.bot_support.screen()
            self.api_call_times["screen"].append(time.time() - t_start)

            # Benchmark tilemap access
            t_start = time.time()
            tilemap = screen.tilemap_background()
            self.api_call_times["tilemap_background"].append(time.time() - t_start)

            # Benchmark sprite list
            t_start = time.time()
            sprites = screen.sprite_list()
            self.api_call_times["sprite_list"].append(time.time() - t_start)

            # Benchmark setting pixels (testing only)
            t_start = time.time()
            screen.set_pixel(80, 72, 3)  # Set a center pixel to test performance
            self.api_call_times["set_pixel"].append(time.time() - t_start)

        # End timing
        end_time = time.time()
        self.duration = end_time - start_time
        self.frames_executed = frames

        # Get final CPU cycles
        self.cpu_cycles_end = self.bot_support.cpu().cycles

        # Calculate result
        result = super().run(0)  # 0 because we've already executed the frames
        return result

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect BotSupport API performance metrics"""
        metrics = {}

        # API call performance statistics
        api_stats = {}
        for api_name, times in self.api_call_times.items():
            if times:
                api_stats[api_name] = {
                    "calls": len(times),
                    "avg_ms": statistics.mean(times) * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000
                }

        metrics["api_performance"] = api_stats

        # Test other API functionality
        screen = self.bot_support.screen()
        cpu = self.bot_support.cpu()

        # Feature availability
        metrics["api_features"] = {
            "screen_available": screen is not None,
            "cpu_available": cpu is not None,
            "tilemap_available": hasattr(screen, "tilemap_background")
        }

        return metrics


class BenchmarkSuite:
    """A collection of benchmarks to run as a suite"""

    def __init__(self, output_dir: str = "benchmark_results"):
        self.benchmarks = []
        self.results = []
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def add_benchmark(self, benchmark: PyBoyBenchmark) -> None:
        """Add a benchmark to the suite"""
        self.benchmarks.append(benchmark)

    def run_all(self) -> List[BenchmarkResult]:
        """Run all benchmarks in the suite"""
        self.results = []

        for benchmark in self.benchmarks:
            print(f"Running benchmark: {benchmark.name} - {benchmark.description}")
            try:
                result = benchmark.run()
                self.results.append(result)
                print(f"  Completed in {result.duration:.2f}s, {result.frames_per_second:.2f} FPS")
            except Exception as e:
                print(f"  Failed: {str(e)}")
            finally:
                benchmark.teardown()

        return self.results

    def save_results(self, filename: str = "benchmark_results.json") -> None:
        """Save benchmark results to a JSON file"""
        path = os.path.join(self.output_dir, filename)

        # Convert results to dictionaries
        results_dict = [asdict(result) for result in self.results]

        with open(path, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"Results saved to {path}")

    def generate_report(self, filename: str = "benchmark_report.txt") -> None:
        """Generate a human-readable report of benchmark results"""
        path = os.path.join(self.output_dir, filename)

        with open(path, 'w') as f:
            f.write("PyBoy Emulator Benchmark Report\n")
            f.write("==============================\n\n")

            # Summary section
            f.write("Summary\n")
            f.write("-------\n")
            f.write(f"Total benchmarks run: {len(self.results)}\n")
            if self.results:
                avg_fps = statistics.mean([r.frames_per_second for r in self.results])
                avg_cps = statistics.mean([r.cycles_per_second for r in self.results])
                f.write(f"Average performance: {avg_fps:.2f} FPS, {avg_cps:.0f} CPU cycles/second\n")
            f.write("\n")

            # Detailed results
            f.write("Detailed Results\n")
            f.write("---------------\n")

            for result in self.results:
                f.write(f"\n{result.name} - {result.description}\n")
                f.write(f"{'-' * (len(result.name) + len(result.description) + 3)}\n")
                f.write(f"Duration: {result.duration:.2f} seconds\n")
                f.write(f"Frames: {result.frames_executed}\n")
                f.write(f"FPS: {result.frames_per_second:.2f}\n")
                f.write(f"CPU Cycles: {result.cpu_cycles}\n")
                f.write(f"Cycles/Second: {result.cycles_per_second:.2f}\n")

                # Display additional metrics if available
                if result.metrics:
                    f.write("\nAdditional Metrics:\n")
                    for metric_name, metric_value in result.metrics.items():
                        # Format metric value based on type
                        if isinstance(metric_value, dict):
                            f.write(f"  {metric_name}:\n")
                            for k, v in metric_value.items():
                                if isinstance(v, float):
                                    f.write(f"    {k}: {v:.4f}\n")
                                elif isinstance(v, dict):
                                    f.write(f"    {k}:\n")
                                    for sub_k, sub_v in v.items():
                                        if isinstance(sub_v, float):
                                            f.write(f"      {sub_k}: {sub_v:.4f}\n")
                                        else:
                                            f.write(f"      {sub_k}: {sub_v}\n")
                                else:
                                    f.write(f"    {k}: {v}\n")
                        elif isinstance(metric_value, float):
                            f.write(f"  {metric_name}: {metric_value:.4f}\n")
                        else:
                            f.write(f"  {metric_name}: {metric_value}\n")

                f.write("\n")

        print(f"Report generated at {path}")


def find_roms(directory: str, extension: str = ".gb") -> List[str]:
    """Find all ROM files in a directory with the given extension"""
    roms = []
    for file in os.listdir(directory):
        if file.lower().endswith(extension):
            roms.append(os.path.join(directory, file))
    return roms


def main():
    """Main function to run the benchmark suite"""
    parser = argparse.ArgumentParser(description="PyBoy Emulator Benchmark Suite")
    parser.add_argument("--rom-dir", type=str, help="Directory containing ROM files to benchmark")
    parser.add_argument("--rom", type=str, help="Path to a specific ROM file to benchmark")
    parser.add_argument("--output-dir", type=str, default="benchmark_results",
                        help="Directory to store benchmark results")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--frames", type=int, default=300, help="Number of frames to run for each benchmark")
    parser.add_argument("--benchmark", type=str, choices=[
        "all", "cpu", "memory", "lcd", "timer", "sound", "cartridge", "botsupport"
    ], default="all", help="Specific benchmark to run")

    args = parser.parse_args()

    # Initialize benchmark suite
    suite = BenchmarkSuite(output_dir=args.output_dir)

    # Collect ROMs to benchmark
    roms_to_benchmark = []
    if args.rom:
        roms_to_benchmark = [args.rom]
    elif args.rom_dir:
        roms_to_benchmark = find_roms(args.rom_dir)
    else:
        # Try to find ROMs in common locations
        possible_dirs = ["roms", "ROMs", ".", "games"]
        for dir_name in possible_dirs:
            if os.path.exists(dir_name):
                roms_to_benchmark.extend(find_roms(dir_name))

        if not roms_to_benchmark:
            print("No ROMs found. Please specify a ROM file or directory.")
            return

    # Add benchmarks for each ROM
    for rom_path in roms_to_benchmark:
        rom_name = os.path.basename(rom_path)
        print(f"Adding benchmarks for {rom_name}")

        # Add different benchmark types based on selection
        if args.benchmark in ["all", "cpu"]:
            suite.add_benchmark(CPUBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "memory"]:
            suite.add_benchmark(MemoryBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "lcd"]:
            suite.add_benchmark(LCDBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "timer"]:
            suite.add_benchmark(TimerBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "sound"]:
            suite.add_benchmark(SoundBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "cartridge"]:
            suite.add_benchmark(CartridgeBenchmark(rom_path, headless=args.headless))

        if args.benchmark in ["all", "botsupport"]:
            suite.add_benchmark(BotSupportBenchmark(rom_path, headless=args.headless))

    # Run all benchmarks
    print(f"Running {len(suite.benchmarks)} benchmarks...")
    suite.run_all()

    # Save results
    suite.save_results()
    suite.generate_report()

    print("Benchmark suite completed!")


if __name__ == "__main__":
    main()







