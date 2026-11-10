import lzma
import struct
import sys

XZ_MAGIC = b"\xfd7zXZ\x00"
MORE_CHUNKS = 1 << 24


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python pbzx_unpack.py <Payload> <output.cpio>")

    src, dst = sys.argv[1], sys.argv[2]
    total = 0

    with open(src, "rb") as f, open(dst, "wb") as out:
        if f.read(4) != b"pbzx":
            sys.exit("Not a pbzx file (missing 'pbzx' header).")

        flags = struct.unpack(">Q", f.read(8))[0]
        chunk_no = 0
        while flags & MORE_CHUNKS:
            flags, length = struct.unpack(">QQ", f.read(16))
            data = f.read(length)
            if len(data) != length:
                sys.exit(f"Truncated file at chunk {chunk_no}.")
            if data[:6] == XZ_MAGIC:
                data = lzma.decompress(data)
            out.write(data)
            total += len(data)
            chunk_no += 1
            if chunk_no % 20 == 0:
                print(f"chunk {chunk_no}, {total / 1e6:.0f} MB written", flush=True)

    print(f"Done: {chunk_no} chunks, {total / 1e6:.0f} MB -> {dst}")


if __name__ == "__main__":
    main()
