const std = @import("std");

pub fn build(b: *std.Build) void {
    const zstd_files = &.{
        "src/sources/zstd-1.5.7/lib/common/debug.c",
        "src/sources/zstd-1.5.7/lib/common/entropy_common.c",
        "src/sources/zstd-1.5.7/lib/common/error_private.c",
        "src/sources/zstd-1.5.7/lib/common/fse_decompress.c",
        "src/sources/zstd-1.5.7/lib/common/xxhash.c",
        "src/sources/zstd-1.5.7/lib/common/zstd_common.c",
        "src/sources/zstd-1.5.7/lib/compress/fse_compress.c",
        "src/sources/zstd-1.5.7/lib/compress/hist.c",
        "src/sources/zstd-1.5.7/lib/compress/huf_compress.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_fast.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_double_fast.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_lazy.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_opt.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_ldm.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_compress.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_compress_literals.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_compress_sequences.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_compress_superblock.c",
        "src/sources/zstd-1.5.7/lib/compress/zstd_preSplit.c",
    };
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "cts",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    exe.linkLibC();
    exe.addIncludePath(.{
        .src_path = .{
            .owner = b,
            .sub_path = "src/sources/zstd-1.5.7/lib",
        },
    });
    exe.addCSourceFiles(.{
        .files = zstd_files,
        .flags = &.{
            "-std=c99",
        },
    });

    b.installArtifact(exe);

    const run_step = b.addRunArtifact(exe);

    b.step("run", "compress time series file").dependOn(&run_step.step);
}
