# cts

The purpose of this program is to test several compression algorithms for time series.

1. Gorilla-style (XOR + RLE of zero bits)
1. Predictor + Shuffle + Zstd
1. Blosc2 with Bitshuffle + LZ4/Zstd

## Problem Statement

We are dealing with time series data describing oscillations of large wind turbine blades,
characterized by narrow-band 1P/3P harmonics, smooth segments, and occasional rare events.
Each series is relatively small: 6001 samples of float32 (~24 KB per series). A strict requirement is
lossless compression (no deviation from original floats at the bit level). The goal is to: Reduce
storage footprint on ZFS while keeping each series as an independent object/file. Ensure extremely
fast decompression for per-series computations. Select an algorithm with established libraries and
solid scientific background.

## Gorilla-style Compression (XOR + RLE)
### Principle
Encodes each float as XOR with previous. If identical → one bit flag. Otherwise stores
differing significant bits. Fully reversible for IEEE-754.

### Performance
- Ratio: 1.8×–4×;
- Decode: 2–5 GB/s;
- Latency: 10–30 μs;
- Cycles/element: 5–15.

### Libraries
- Facebook Beringei (archived),
- Apache Parquet encoders.

### Reference
Tu, Y., et al. Gorilla: A Fast, Scalable, In-Memory Time Series Database. VLDB 2015.
- URL: [https://www.vldb.org/pvldb/vol8/p1816-teller.pdf](https://www.vldb.org/pvldb/vol8/p1816-teller.pdf)

### Risk Assessment
#### Strengths
very simple, fast

#### Risks
archived project, weak community support, custom tooling required.

#### Risk level
Medium.

## Predictor + Shuffle + Zstd
### Principle
Second-order predictor residuals → byte/bit shuffle → Zstd (levels 1–3).

### Performance
- Ratio: 1.6×–3.5×;
- Decode: 2–4 GB/s;
- Latency: 36–66 μs; 
- Cycles/element: 18–33.

### Libraries
- Zstandard (C),
- zig-zstd,
- Blosc2 integration.

### Reference
Collet, Y. Zstandard — Real-time compression algorithm, 2016.
- URL: [https://facebook.github.io/zstd/](https://facebook.github.io/zstd/ );

Alted, F. Blosc: A High Performance Compressor, 2010.
- URL: [https://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf](https://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf)

### Risk Assessment
#### Strengths
strong ecosystem, corporate support.

#### Risks
slightly more complex pipeline.

#### Risk level
Low.

## Blosc2 (Bitshuffle + LZ4/Zstd)
### Principle
Splits data into chunks, applies bitshuffle, compresses with LZ4 (fast) or Zstd (ratio).

### Performance
- Ratio: LZ4 1.3×–2.3×, Zstd 1.6×–3×;
- Decode: LZ4 6–10 GB/s, Zstd 2–4 GB/s;
- Latency: 16–40 μs;
- Cycles/element: 8–20.

### Libraries
- c-blosc2 (C), used in HDF5, NumPy.

### Reference
Alted, F., Vilata, I. The Blosc data compressor, 2010–2021.
- URL: [https://www.blosc.org/](https://www.blosc.org/);

Collet, Y. LZ4, 2013.
- URL: [https://lz4.github.io/lz4/](https://lz4.github.io/lz4/)

### Risk Assessment
#### Strengths
actively maintained, scientific adoption.

#### Risks
smaller community, container complexity.

#### Risk level
Low–Medium.

Algorithm      | Ratio     | Decode Speed | Latency  | Cycles/element | Risk
---------------|-----------|--------------|----------|----------------|-----------
Gorilla-style  | 1.8×–4×   | 2–5 GB/s     | 10–30 μs | 5–15           | Medium
Predictor+Zstd | 1.6×–3.5× | 2–4 GB/s     | 36–66 μs | 18–33          | Low
Blosc2 (LZ4)   | 1.3×–2.3× | 6–10 GB/s    | 16–24 μs | 8–12           | Low–Medium
Blosc2 (Zstd)  | 1.6×–3×   | 2–4 GB/s     | 20–40 μs | 10–20          | Low–Medium


## Executive Summary
- The dataset: wind turbine blade oscillation series (narrow-band harmonics + rare events),
requiring strictly lossless compression.
- Gorilla-style: optimal for lowest latency decode, but riskier due to weak ecosystem.
- Predictor+Zstd: best balance, safest long-term choice, backed by industry.
- Blosc2: excellent for multi-thread throughput and integration in scientific pipelines.

