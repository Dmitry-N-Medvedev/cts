const std = @import("std");
const c = @cImport({
    @cInclude("zstd.h");
});

pub fn main() !void {
    std.debug.print("hi\n", .{});
}
