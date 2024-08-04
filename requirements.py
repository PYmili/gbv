with open("requirements.txt", encoding="utf-8") as f:
    print("[")
    for line in f.readlines():
        print("\t" + f"\"{line.split("==")[0]}\"", end=",\n")
    print("]")
