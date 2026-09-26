/* Validate the actual Defold archive in an APK, using its matching Bob jar.
 * Usage: java -cp bob.jar tools/VerifyTexturePayloads.java --apk game.apk
 *     or java -cp bob.jar tools/VerifyTexturePayloads.java --archive build/default/game
 */
import com.dynamo.bob.archive.ArchiveReader;
import com.dynamo.graphics.proto.Graphics.TextureImage;
import net.jpountz.lz4.LZ4Factory;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Comparator;
import java.util.zip.ZipFile;

class VerifyTexturePayloads {
    static void verifyTexture(String name, byte[] bytes) throws Exception {
        if (bytes.length < 4) throw new IOException(name + ": missing texture header");
        int size = ByteBuffer.wrap(bytes, 0, 4).order(ByteOrder.LITTLE_ENDIAN).getInt();
        if (size <= 0 || size > bytes.length - 4)
            throw new IOException(name + ": truncated texture header");
        var image = TextureImage.parseFrom(Arrays.copyOfRange(bytes, 4, size + 4));
        if (image.getAlternativesCount() == 0)
            throw new IOException(name + ": no texture alternatives");
        long required = 0;
        for (var alternative : image.getAlternativesList()) {
            required += Integer.toUnsignedLong(alternative.getDataSize());
        }
        long actual = bytes.length - size - 4L;
        if (required != actual) {
            throw new IOException(name + ": texture payload is " + actual
                + " bytes, but its header requires " + required + " bytes");
        }
        System.out.println("PASS: " + name + " complete texture payload: " + actual + " bytes");
    }

    static void verifyArchive(Path prefix) throws Exception {
        var reader = new ArchiveReader(prefix + ".arci", prefix + ".arcd", prefix + ".dmanifest");
        int textures = 0;
        try (var data = new RandomAccessFile(prefix + ".arcd", "r")) {
            reader.read();
            for (var entry : reader.getEntries()) {
                if (!entry.getFilename().endsWith(".texturec")) continue;
                if (entry.isEncrypted()) throw new IOException("Encrypted texture is unsupported by this verifier");
                int storedSize = entry.isCompressed() ? entry.getCompressedSize() : entry.getSize();
                if (storedSize < 0 || entry.getSize() < 0 || entry.getResourceOffset() < 0
                    || entry.getResourceOffset() > data.length() - storedSize)
                    throw new IOException(entry.getFilename() + ": incomplete archive entry");
                byte[] stored = new byte[storedSize];
                data.seek(entry.getResourceOffset());
                data.readFully(stored);
                byte[] bytes = stored;
                if (entry.isCompressed()) {
                    bytes = new byte[entry.getSize()];
                    int decoded = LZ4Factory.safeInstance().safeDecompressor()
                        .decompress(stored, 0, stored.length, bytes, 0, bytes.length);
                    if (decoded != bytes.length) throw new IOException("Incomplete texture decompression");
                }
                verifyTexture(entry.getFilename(), bytes);
                textures++;
            }
        } finally {
            reader.close();
        }
        if (textures == 0) throw new IOException("No archived textures were checked");
        System.out.println("PASS: verified " + textures + " archived texture(s)");
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2 || !(args[0].equals("--apk") || args[0].equals("--archive")))
            throw new IllegalArgumentException("Use --apk FILE or --archive PATH/game");
        if (args[0].equals("--archive")) {
            verifyArchive(Path.of(args[1]));
            return;
        }
        Path temp = Files.createTempDirectory("fruit-apk-check-");
        try (var apk = new ZipFile(args[1])) {
            for (String suffix : new String[]{"arci", "arcd", "dmanifest"}) {
                var entry = apk.getEntry("assets/game." + suffix);
                if (entry == null) throw new IOException("APK lacks assets/game." + suffix);
                try (var input = apk.getInputStream(entry)) {
                    Files.copy(input, temp.resolve("game." + suffix));
                }
            }
            verifyArchive(temp.resolve("game"));
        } finally {
            try (var files = Files.walk(temp)) {
                for (var path : files.sorted(Comparator.reverseOrder()).toList()) Files.deleteIfExists(path);
            }
        }
    }
}
