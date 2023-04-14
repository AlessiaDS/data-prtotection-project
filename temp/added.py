#To add to Incognito!

def at_last(check):
    count = 0
    for i in check:
        if check[i] == 0: count +=1
    if count == len(check): return True
    return False

def mono_attr_verify(graph, qi_names, qi_heights, k, dghs, qi_frequency, data):

    # vertex text format "qi_name:lv;qi_name:lv;..."
    kanon_prev = False

    for i in range(len(qi_names)):
        for j in range(qi_heights[i]):
            node = str(qi_names[i] + ":" + j)
            graph.addVertex(node)
            if not kanon_prev:
                graph.setData(node, generalize(qi_names, dghs, qi_frequency, data))
                if is_k_anon(graph.getData(node), k):
                    graph.setMark(node)
                    kanon_prev = True
            else:
                graph.setMark(node)
                kanon_prev = False

    return

#data contains the generalization levels -> combination to generalize to
def generalize(qi_names, dghs, og_frequency, data):
    #print("Current <COMB>: ", data)

    qi_frequency = og_frequency

    # Look up table for the generalized values, to avoid searching in hierarchies:
    generalizations = dict()
    # Generalized value to apply for the needed lables
    generalized_value = dict()
    # Note: using the list of keys since the dictionary is changed in size at runtime
    # and it can't be used as an iterator:
    for j, qi_sequence in enumerate(list(qi_frequency)):
        if j == 0: continue
        # Get the generalized value:
        for i in range(len(data)):
            # If QI is going back to genLv 0 then do nothing since it has already been "rolled back" with resetState
            # If old and new level are the same then do nothing once again
            if data[i] != 0:
                if qi_sequence[i] in generalizations:
                    # Find directly the generalized value in the look up table:
                    generalized_value[i] = generalizations[i]
                else:
                    # Get the corresponding generalized value from the attribute DGH:
                    try:
                        generalized_value[i] = dghs[qi_names[i]] \
                            .generalize_jump(
                            qi_sequence[i], 0,
                            data[i])
                    except KeyError as error:
                        # print("Error: ",error)
                        return
                    if generalized_value[i] is None:
                        # Skip if it's a hierarchy root:
                        continue

                # Add to the look-up table:
                generalizations[i] = generalized_value[i]

        # Skip if header of Table
        if qi_sequence == None: continue

        # Tuple with generalized value:
        new_qi_sequence = list(qi_sequence)
        # Change only the attributes that need to be changed -> the ones with a generalization level different from before
        for id, gen_val in generalized_value.items():
            new_qi_sequence[id] = gen_val
        new_qi_sequence = tuple(new_qi_sequence)

        # TODO: TO GENETALIZE! (0,0,0) IS NOT GENERAL (might actually be already managed by the first "if")
        # If start of cycle no need to change or apply anything
        if data != (0, 0, 0):
            # Check if there is already a tuple like this one:
            if new_qi_sequence in qi_frequency:
                # Update the already existing one:
                # Update the number of occurrences:
                occurrences = qi_frequency[new_qi_sequence][0] \
                              + qi_frequency[qi_sequence][0]
                # Unite the row indices sets:
                rows_set = qi_frequency[new_qi_sequence][1] \
                    .union(qi_frequency[qi_sequence][1])
                qi_frequency[new_qi_sequence] = (occurrences, rows_set)
                # Remove the old sequence:
                qi_frequency.pop(qi_sequence)
            else:
                # Add new tuple and remove the old one:
                qi_frequency[new_qi_sequence] = qi_frequency.pop(qi_sequence)
    return qi_frequency
