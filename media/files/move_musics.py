from glob import  glob
import shutil
import os

target = "Amir Eid/"
path = glob("./*/*/*.m4a")
done_count = 0
errors_count = 0

def get_file_name(file):
    return os.path.basename(file).split('.')[0] 



for file in path:
    done_count += 1 
    file_name = get_file_name(file)
    try:
        shutil.move(file,target+file_name+".m4a")
    except:
        print("Error with file: "+ file_name)
        errors_count += 1
print("Done:",done_count)
print(f"{errors_count} error")