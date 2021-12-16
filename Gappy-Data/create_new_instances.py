import os
import random
from minizinc import Instance, Model, Solver
from datetime import datetime

DEBUG = False
now = datetime.now()


def create_directory(dir_name, ask_to_override = True):
    if not os.path.isdir(dir_name):        
        os.mkdir(dir_name)
        return True
    elif ask_to_override:
        c = input("Might override files in directory '" + dir_name + "', do you want to continue? (y/n)")
        if c != 'y':
            print("Aborting.")
            return False
        else:
            return True
    return True


# creates file in output format
def create_dzn(hints : list, file_name: str):
    size = int(len(hints)/2)

    temp = open(file_name, "w+")
    temp.write("size = " + str(size) + ";\n\n")

    temp.write("clue_h = \n  [" + str(hints[0]))
    for i in range(1,size):
        temp.write(", " + str(hints[i]))

    temp.write("];\n\n  clue_v = \n  [" + str(hints[size]))
    for i in range(size+1,2*size):
        temp.write(", " + str(hints[i]))
    temp.write("];")
    
    temp.close()


def create_radom_hints(size, num_hints):
    # check if num_hints is  meaningful
    if(num_hints < 2):
        num_hints = 2
    if(num_hints > size*2):
        num_hints = size*2

    # create num_hint hints
    hint_indices = list(random.sample(range(1, size*2+1), num_hints))

    # check if there is at least one hint in each array (minizinc constraint for opts)
    hint_in_first = False
    hint_in_second = False
    for e in hint_indices:
        if e < size:
            hint_in_first = True
        else:
            hint_in_second = True
    if not hint_in_first:
        hint_indices[0]  = hint_indices[0]-size
    if not hint_in_second:
        hint_indices[0]  = hint_indices[0]+size

    # create output array
    hints = []
    for i in range(0, size*2):
        if i in hint_indices: 
            hints.append(' ' + str(random.randint(1,size-2)))
        else:
            hints.append('<>')
    
    return hints


# returns all solutions for a dzn file
def get_all_solutions(data_file):
    gecode = Solver.lookup("gecode")
    model = Model('../gaps.mzn')
    model._add_file(data_file)
    instance = Instance(gecode, model)
    result = instance.solve(all_solutions=True)
    if DEBUG:
        print(result)

    solutions = []

    for i in range(len(result)):
        solutions.append(result[i, "assign"])
    
    return(solutions)


# returns the full hint for a given gameboard
def get_full_hints(sol : list):
    size = len(sol)
    hints = []                  # first column then row hints
    for i in range(0,size*2):
        hints.append(-1)

    r = 0
    c = 0
    for row in sol:
        for element in row:
            if element:
                # update hint for column
                if(hints[c+size] == -1):
                    hints[c+size] = r
                else:
                    hints[c+size] = r-hints[c+size]-1
                # update hint for row
                if(hints[r] == -1):
                    hints[r] = c
                else:
                    hints[r] = c-hints[r]-1
            c +=1
        r += 1
        c = 0   

    return hints


# checks if hints yied exactly one solution and creates dzn file if so
def check_if_instance(hint : list, file_name : str):
    create_dzn(hint, 'temp/temp.dzn')
    num_sol = len(get_all_solutions('temp/temp.dzn'))
    if num_sol == 1:
        command = 'mv ' + 'temp/temp.dzn' + ' ' + file_name
        os.system(command)
        return True
    else:
        return False


# makes a partial hint form hint
def remove_hints(hint : list, count : int):
    size = int(len(hint)/2)
    if count > size*1.5:
        count = size*1.5
    if count < 0:
        return False
    # create num_hint hints
    rm_indices = list(random.sample(range(0, size*2), count))

    # check if there is at least one hint left in each array (minizinc constraint for opts)    
    hint_in_first = False
    hint_in_second = False
    for i in range(0, size):
        if i not in rm_indices:
            hint_in_first = True
    for i in range(size, size*2):
        if i not in rm_indices:
            hint_in_second = True
    if not hint_in_first:
        rm_indices[0]  = rm_indices[0]-size
    if not hint_in_second:
        rm_indices[0]  = rm_indices[0]+size
    
    for index in rm_indices:
        hint[index] = '<>'
    
    return True



def main():
    if not create_directory("temp"):
        return
    if not create_directory("created_instances", False):
        os.system("rmdir temp")
    new_dir = "created_instances/"+str(now.strftime("%d-%m_%H-%M-%S"))
    if not create_directory(new_dir):
        os.system("rmdir temp")
        os.system("rmdir created_instances --ignore-fail-on-non-empty")
        return

    try:
        # some parameters
        size = 10
        num_hints_start = 4

        # create some possible gameboards
        print("Creating possible games ...")
        hints = create_radom_hints(size, num_hints_start)
        create_dzn(hints, "temp/start.dzn")
        solutions = get_all_solutions("temp/start.dzn")

        # for created gameboards create hints and write to file if they only have one solution
        print("Creating datafiles ", end = "")
        full_hints  = []
        ctr = 0
        for sol in solutions:
            full_hints.append(get_full_hints(sol))
            file_name = new_dir + '/level1_'+str(ctr)+'.dzn'
            if check_if_instance(full_hints[ctr], file_name):
                ctr += 1
                print(".", end = "")
            else:
                full_hints.pop()
        
        # create partial hints and write to files
        print("\nCreating datafiles for level 2 ", end = "")
        ctr = 0
        for hint in full_hints:
            # remove some hints and write to partial_hints
            partial_hint = hint
            if remove_hints(partial_hint, 5):
                file_name = new_dir + '/level2_'+str(ctr)+'.dzn'
                if check_if_instance(partial_hint, file_name):
                    ctr += 1
                    print(".", end = "")
        print("\n")

        print("found " + str(len(full_hints)) + " gameboards(s)")
        
    except:
        print('error.')
    finally:
        # clean up directories    
        os.system("rm temp/*")
        os.system("rmdir temp")
        command = "rmdir " + new_dir + " --ignore-fail-on-non-empty"
        os.system(command)
        os.system("rmdir created_instances --ignore-fail-on-non-empty")

main()
