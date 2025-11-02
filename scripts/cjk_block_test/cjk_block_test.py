def cjk_block_check():
    UN_DEF_CH = "Unicode未收錄字符"
    OTHER_CH = "其他字符"
    unicode_range = (
        ((0x4E00, 0x9FFF), "Unicode CJK基本區"),
        ((0x3400, 0x4DBF), "Unicode CJK擴展A區"),
        ((0x20000, 0x2A6DF), "Unicode CJK擴展B區"),
        ((0x2A700, 0x2B739), "Unicode CJK擴展C區"),
        ((0x2B740, 0x2B81D), "Unicode CJK擴展D區"),
        ((0x2B820, 0x2CEAD), "Unicode CJK擴展E區"),
        ((0x2CEB0, 0x2EBE0), "Unicode CJK擴展F區"),
        ((0x30000, 0x3134A), "Unicode CJK擴展G區"),
        ((0x31350, 0x323AF), "Unicode CJK擴展H區"),
        ((0x2EBF0, 0x2EE5D), "Unicode CJK擴展I區"),
        ((0x323B0, 0x33479), "Unicode CJK擴展J區"),
        ((0xF900, 0xFAFF), "Unicode CJK相容表意字符"),
        ((0x2F800, 0x2FA1F), "Unicode CJK相容表意字符增補"),
        ((0x2F00, 0x2FDF), "Unicode CJK康熙部首"),
        ((0x2E80, 0x2EFF), "Unicode CJK康熙部首增補"),
        ((0x31C0, 0x31EF), "Unicode CJK筆劃"),
        ((0x2FF0, 0x2FFF), "表意文字描述符號"),
        ((0x3040, 0x309F), "日文平假名"),
        ((0x30A0, 0x30FF), "日文片假名"),
        ((0xE000, 0xF8FF), "Unicode 私人使用區"),
        ((0xF0000, 0xFFFFD), "Unicode 私人使用區"),
        ((0x100000, 0x10FFFFD), "Unicode 私人使用區"),
    )
    block_dic = {UN_DEF_CH: 0, OTHER_CH: 0}
    filter_set = set()
    unified_ideo_set = set(map(chr, range(0x4E00, 0xA000)))

    with open('./file_to_check.txt', 'r', encoding='utf8') as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split('\t', 1)
            if not parts:
                continue
            ch = parts[0].strip()
            if not ch:
                continue
            if len(ch) > 1:
                block_dic[UN_DEF_CH] += 1
                continue

            if ch in filter_set:
                continue

            ch_ord = ord(ch)
            for (lower, upper), block_name in unicode_range:
                if lower <= ch_ord <= upper:
                    block_dic[block_name] = block_dic.get(block_name, 0) + 1
                    if block_name in ("Unicode CJK相容表意字符", "Unicode CJK相容表意字符增補"):
                        print(f"存在兼容區字符：{ch}")
                    unified_ideo_set.discard(ch)
                    filter_set.add(ch)
                    break
            else:
                block_dic[OTHER_CH] += 1

    print("\n=== 統計結果（按區段名稱字母序） ===")
    print("| Unicode區塊 | 字數 |")
    print("| :---: | :---: |")
    for block_name, count in sorted(block_dic.items(), key=lambda x: x[0]):
        print(f"| {block_name} | {count} |")

    print("\n=== 基本區缺字統計 ===")
    missing_count = len(unified_ideo_set)
    if missing_count:
        preview = "".join(sorted(unified_ideo_set))
        print(f"缺少以下基本區漢字（共 {missing_count} 字）：{preview}")
    else:
        print("基本區漢字無缺漏。")


if __name__ == "__main__":
	cjk_block_check()