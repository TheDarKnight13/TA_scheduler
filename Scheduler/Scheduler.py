from ortools.sat.python import cp_model
from itertools import groupby
import csv
import argparse 

def cluster_score(binary_list):
    # Initialize variables
    clusters = [sum(g) for _, g in groupby(binary_list)]
    score = len(binary_list)/len(clusters) 
    return score

def schedule_generator(num_TAs,num_days,num_slots,shift_requests,name_mapping,day_names, slot_names,file_name):
    #Creating the model
    model = cp_model.CpModel()
    
    #Creating the variables
    """"
    0,1,0 gives the same score as 1,0,1 despite the former being better
    To overcome this, I add an extra slot at the start which no one takes
    Now, 0*,0,1,0 gives a higher score than 0*,1,0,1
    """
    shifts = {}
    for n in range(num_TAs):
        for d in range(num_days):
            for s in range(num_slots[d]+1): #Adding an extra slot at the start
                shifts[(n, d, s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")
                
    #Constraint that there is exactly two TAs in a shift
    for d in range(num_days):
        for s in range(1,num_slots[d]+1):
            model.add(sum(shifts[(n,d,s)] for n in range(num_TAs)) == 2)
    
    #Constraint that no one takes the zeroth shift
    for d in range(num_days):
        model.add(sum(shifts[(n,d,0)] for n in range(num_TAs)) == 0)    
    
    
    # Try to distribute the shifts evenly
    min_slots_per_TA = (2*sum(num_slots)) // num_TAs

    if 2*sum(num_slots) % num_TAs == 0:
        max_slots_per_TA = min_slots_per_TA
    else:
        max_slots_per_TA = min_slots_per_TA + 1

    for n in range(num_TAs):
        num_slots_worked = 0
        for d in range(num_days):
            for s in range(1,num_slots[d]+1):
                num_slots_worked += shifts[(n, d, s)]
        model.add(min_slots_per_TA <= num_slots_worked)
        model.add(num_slots_worked <= max_slots_per_TA)
    
    #Objective function
    model.maximize(
        sum(
            shift_requests[n][d][s] * shifts[(n, d, s+1)]
            for n in range(num_TAs)
            for d in range(num_days)
            for s in range(num_slots[d])
        )*100 + 

        sum(
            cluster_score([shifts[(n,d,s)] for s in range(num_slots[d]+1)])
            for n in range(num_TAs)
            for d in range(num_days)    
        )
    )
    
    #Solving the problem
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    
    #Printing a solution
    f = open(file_name.split(".")[0]+".txt", "w")
   
    if status == cp_model.OPTIMAL:
        for d in range(num_days):
            f.write(day_names[d]+"\n")
            for s in range(1,num_slots[d]+1):
                f.write(slot_names[d][s-1]+"\n")
                for n in range(num_TAs):            
                    if solver.value(shifts[(n, d, s)]) == 1:
                        if shift_requests[n][d][s-1] == 1:
                            f.write(name_mapping[n]+"\n")
                        else:
                            f.write(name_mapping[n]+"(not requested). \n")
                f.write("\n")
            f.write("\n")
        f.write("Number of slot requests met = " + str(int(solver.objective_value/100)) + "(out of "+str(2*sum(num_slots))+")")
    else:
        f.write("No optimal solution found !")
        
    f.close()

def read_file(file_name):
    shift_requests = []
    name_mapping = {}

    with open(file_name, mode ='r') as file:
        csvFile = csv.reader(file)
        for i,line in enumerate(csvFile):
            if i==0: #Reads the names of each TA
                day_names = [x for x in line if len(x)!=0]  #List that maps each day number to a day name

            elif i==1: #Reads all the time slots across days
                slot_names = []
                temp = []
                for j in range(1,len(line)):
                    if line[j]=="":
                        slot_names.append(temp)
                        temp = []

                    else:
                        temp.append(line[j])

                slot_names.append(temp)

            else:  #Reads the availability of each TA
                name_mapping[i-2] = line[0]
                slots = []
                temp = []
                for j in range(1,len(line)):
                    if line[j] == "":
                        slots.append(temp)
                        temp = []

                    else:
                        temp.append(int(line[j]))

                slots.append(temp)
                shift_requests.append(slots)     

    num_TAs = len(shift_requests)
    num_days = len(shift_requests[0])
    num_slots = [len(x) for x in shift_requests[0]]
    
    return shift_requests, name_mapping, num_TAs, num_days, num_slots, day_names, slot_names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file_name",type=str)
    args = parser.parse_args()

    file_name1 = args.file_name
    shift_requests1, name_mapping1, num_TAs1, num_days1, num_slots1, day_names1, slot_names1 = read_file(file_name1)

    print("The number of TAs are "+str(num_TAs1))
    print("The number of days are "+str(num_days1))
    print("The number of slots in each day are:")
    print(num_slots1)
    
    schedule_generator(num_TAs1,num_days1,num_slots1,shift_requests1,name_mapping1,day_names1, slot_names1,file_name1)
    print("The schedule is at "+args.file_name.split(".")[0]+".txt")

if __name__ == "__main__":
    main()

