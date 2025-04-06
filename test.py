import gemini_caller

if __name__ == '__main__':
    print("--- Response ---")
    print(gemini_caller.codegen_process_data("Find the mean value in the array my_array"))
    print("----------------")