import csv
import sys
from io import StringIO
import datafly
import MyGraph as mg
from dgh import CsvDGH
import copy

class _Table:

    def __init__(self, pt_path: str, dgh_paths: dict):

        """
        Instantiates a table and the specified Domain Generalization Hierarchies from the
        corresponding files.

        :param pt_path:             Path to the table to anonymize.
        :param dgh_paths:           Dictionary whose values are paths to DGH files and whose keys
                                    are the corresponding attribute names.
        :raises IOError:            If a file cannot be read.
        :raises FileNotFoundError:  If a file cannot be found.
        """

        self.table = None
        """
        Reference to the table file.
        """
        self.attributes = dict()
        """
        Dictionary whose keys are the table attributes names and whose values are the corresponding
        column indices.
        """
        self._init_table(pt_path)
        """
        Reference to the table file.
        """
        self.dghs = dict()
        """
        Dictionary whose values are DGH instances and whose keys are the corresponding attribute 
        names.
        """
        for attribute in dgh_paths:
            self._add_dgh(dgh_paths[attribute], attribute)

    def __del__(self):

        """
        Closes the table file.
        """

        self.table.close()

    @staticmethod
    def _log(content, enabled=True, endl=True):

        """
        Prints a log message.

        :param content: Content of the message.
        :param enabled: If False the message is not printed.
        """

        if enabled:
            if endl:
                print(content)
            else:
                sys.stdout.write('\r' + content)

    @staticmethod
    def _debug(content, enabled=False):

        """
        Prints a debug message.

        :param content: Content of the message.
        :param enabled: If False the message is not printed.
        """

        if enabled:
            print(content)

    def _init_table(self, pt_path: str):

        """
        Gets a reference to the table file and instantiates the attribute dictionary.

        :param pt_path:             Path to the table file.
        :raises IOError:            If the file cannot be read.
        :raises FileNotFoundError:  If the file cannot be found.
        """

        try:
            self.table = open(pt_path, 'r')
        except FileNotFoundError:
            raise

    def _get_values(self, row: str, attributes: list, row_index=None):

        """
        Gets the values corresponding to the given attributes from a row.

        :param row:         Line of the table file.
        :param attributes:  Names of the attributes to get the data of.
        :param row_index:   Index of the row in the table file.
        :return:            List of corresponding values if valid, None if this row must be ignored.
        :raises KeyError:   If an attribute name is not valid.
        :raises IOError:    If the row cannot be read.
        """

        # Ignore empty lines:
        if row.strip() == '':
            return None

    def _set_values(self, row, values, attributes: list) -> str:

        """
        Sets the values of a row for the given attributes and returns the row as a formatted string.

        :param row:         List of values of the row.
        :param values:      Values to set.
        :param attributes:  Names of the attributes to set.
        :return:            The new row as a formatted string.
        """

        pass

    def _add_dgh(self, dgh_path: str, attribute: str):

        """
        Adds a Domain Generalization Hierarchy to this table DGH collection, from its file.

        :param dgh_path:            Path to the DGH file.
        :param attribute:           Name of the attribute with this DGH.
        :raises IOError:            If the file cannot be read.
        :raises FileNotFoundError:  If the file cannot be found.
        """

        pass

class CsvTable(_Table):

    def __init__(self, pt_path: str, dgh_paths: dict):

        super().__init__(pt_path, dgh_paths)

    def __del__(self):

        super().__del__()

    def anonymize(self, qi_names, k, output_path, v=False):

        super().anonymize(qi_names, k, output_path, v)

    def _init_table(self, pt_path):

        super()._init_table(pt_path)

        try:
            # Try to read the first line (which contains the attribute names):
            csv_reader = csv.reader(StringIO(next(self.table)))
        except IOError:
            raise

        # Initialize the dictionary of table attributes:
        for i, attribute in enumerate(next(csv_reader)):
            self.attributes[attribute] = i

    def _get_values(self, row: str, attributes: list, row_index=None):

        super()._get_values(row, attributes, row_index)

        # Ignore the first line (which contains the attribute names):
        if row_index is not None and row_index == 0:
            return None

        # Try to parse the row:
        try:
            csv_reader = csv.reader(StringIO(row))
        except IOError:
            raise
        parsed_row = next(csv_reader)

        values = list()
        for attribute in attributes:
            if attribute in self.attributes:
                values.append(parsed_row[self.attributes[attribute]])
            else:
                raise KeyError(attribute)

        return values

    def _set_values(self, row: list, values, attributes: list):

        for i, attribute in enumerate(attributes):
            row[self.attributes[attribute]] = values[i]

        values = StringIO()
        csv_writer = csv.writer(values)
        csv_writer.writerow(row)

        return values.getvalue()

    def _add_dgh(self, dgh_path, attribute):

        try:
            self.dghs[attribute] = CsvDGH(dgh_path)
        except FileNotFoundError:
            raise
        except IOError:
            raise

    def old_anonymize(self, qi_names: list, k: int):

        """
        Writes a k-anonymous representation of this table on a new file. The maximum number of
        suppressed rows is k.

        :param qi_names:    List of names of the Quasi Identifiers attributes to consider during
                            k-anonymization.
        :param k:           Level of anonymity.
        :param output_path: Path to the output file.
        :param v:           If True prints some logging.
        :raises KeyError:   If a QI attribute name is not valid.
        :raises IOError:    If the output file cannot be written.
        """

        # Start reading the table file (the one to anonymize) from the top:
        self.table.seek(0)

        # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
        # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
        # containing the indices of the rows in the original table file with those QI values:
        qi_frequency = dict()  # K = Tuple ("a1","b2","c1") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # sets containing the corresponding domain elements:
        domains = dict()  # K = 0,1,2,... "Index" of QI, V = set {QI_val 1, QI_val 2, ...}
        for i, attribute in enumerate(qi_names):
            domains[i] = set()

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # the current levels of generalization, from 0 (not generalized):
        gen_levels = dict()
        for i, attribute in enumerate(qi_names):
            gen_levels[i] = 0

        # Initialize qi_frequency
        for i, row in enumerate(self.table):
            # i = index row
            # row value
            qi_sequence = self._get_values(row, qi_names, i)  # list of values contained in qi_names at row 'i'

            # Skip if this row must be ignored:
            if qi_sequence is None:
                continue
            else:
                qi_sequence = tuple(qi_sequence)  # list -> tuple ("val_a","val_b","val_c")

            if qi_sequence in qi_frequency:  # if qi_val_combination in qi_frequency Key
                occurrences = qi_frequency[qi_sequence][0] + 1  # add occurence of qi_sequence
                rows_set = qi_frequency[qi_sequence][1].union([i])  # add index
                qi_frequency[qi_sequence] = (occurrences, rows_set)  # update value
            else:
                # Initialize number of occurrences and set of row indices:
                qi_frequency[qi_sequence] = (1, set())
                qi_frequency[qi_sequence][1].add(i)

                # Update domain set for each attribute in this sequence:
                for j, value in enumerate(qi_sequence):
                    domains[j].add(value)  # j = "index" of a qi attribute

        while True:

            # Number of tuples which are not k-anonymous.
            count = 0

            for qi_sequence in qi_frequency:  # iterate through the Keys

                # Check number of occurrences of this sequence:
                if qi_frequency[qi_sequence][0] < k:
                    # Update the number of tuples which are not k-anonymous:
                    count += qi_frequency[qi_sequence][0]

            # Limit the number of tuples to suppress to k:
            if count > k:

                # Get the attribute whose domain has the max cardinality:
                max_cardinality, max_attribute_idx = 0, None
                for attribute_idx in domains:  # iterate through the Keys
                    if len(domains[attribute_idx]) > max_cardinality:
                        max_cardinality = len(domains[attribute_idx])
                        max_attribute_idx = attribute_idx

                # Index of the attribute to generalize:
                attribute_idx = max_attribute_idx

                # Generalize each value for that attribute and update the attribute set in the
                # domains dictionary:
                domains[attribute_idx] = set()
                # Look up table for the generalized values, to avoid searching in hierarchies:
                generalizations = dict()

                # Note: using the list of keys since the dictionary is changed in size at runtime
                # and it can't be used an iterator:
                for j, qi_sequence in enumerate(list(qi_frequency)):

                    # Get the generalized value:
                    if qi_sequence[attribute_idx] in generalizations:
                        # Find directly the generalized value in the look up table:
                        generalized_value = generalizations[attribute_idx]
                    else:
                        # Get the corresponding generalized value from the attribute DGH:
                        try:
                            generalized_value = self.dghs[qi_names[attribute_idx]] \
                                .generalize(
                                qi_sequence[attribute_idx],
                                gen_levels[attribute_idx])
                        except KeyError as error:
                            return

                        if generalized_value is None:
                            # Skip if it's a hierarchy root:
                            continue

                        # Add to the look up table:
                        generalizations[attribute_idx] = generalized_value
                        # probably instead of "attribute_idx" you should use "qi_sequence[attribute_idx]"

                    # Tuple with generalized value:
                    new_qi_sequence = list(qi_sequence)
                    new_qi_sequence[attribute_idx] = generalized_value
                    new_qi_sequence = tuple(new_qi_sequence)

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

                    # Update domain set with this attribute value:
                    domains[attribute_idx].add(qi_sequence[attribute_idx])

                # Update current level of generalization:
                gen_levels[attribute_idx] += 1

                '''print(gen_levels)
                for key in qi_frequency:
                    print("Key: ", key, "; Reps: ", qi_frequency[key][0], ", Set of rows: ", qi_frequency[key][1])
                print("end if")'''

            else:
                break
        return qi_frequency

        # ---------------------------BEGINNING---------------------------
    def anonymize(self, qi_names, k: int, v=True):

            """
            Writes a k-anonymous representation of this table on a new file. The maximum number of
            suppressed rows is k.

            :param qi_names:    List of names of the Quasi Identifiers attributes to consider during
                                k-anonymization.
            :param k:           Level of anonymity.
            :param output_path: Path to the output file.
            :param v:           If True prints some logging.
            :raises KeyError:   If a QI attribute name is not valid.
            :raises IOError:    If the output file cannot be written.
            """

            '''try:
                output = open(output_path, 'w')
            except IOError:
                raise'''

            print("Start Anon")

            self.table.seek(0)

            # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
            # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
            # containing the indices of the rows in the original table file with those QI values:
            qi_frequency = dict()  # K = Tuple ("a","b","c") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

            # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
            # the current levels of generalization, from 0 (not generalized):
            gen_levels = dict()

            k_anon_queue = dict()

            qi_frequency = generate_frequency(self, qi_names)

            # ---------------------------START PART 1 - Generalization---------------------------

            # TODO: GENERALIZE CALL

            #print("Used K: ",k)

            qi_heights = dict()

            graph = mg.MyDiGraph()

            #TODO: TO ADD
            for i in qi_names:
                qi_heights[i] = CsvDGH.get_tree_height(table.dghs[i]) + 1

            mono_attr_verify(self, graph, qi_names, qi_heights, k, table.dghs, k_anon_queue)
            #print("k_anon_queue content: ",k_anon_queue)
            #graph.printOut()

            print("End Anon")

# :param table: table to check anonymization
# :param k: level of anonymization
# check if table is k-anon
# meaning check if there are less than k sequences that have a repetition lower than k
def is_k_anon(table, k):
    count = 0 # non k-anon touples count
    for key in table:
        if table[key][0] < k:
            count += table[key][0]
    return count <= k

def generate_frequency(csvtable, qi_names):
    #print("ENTER gen_freq")
    #print("Names given: ",qi_names)
    csvtable.table.seek(0)
    qi_frequency = dict()
    # Initialize qi_frequency
    for i, row in enumerate(csvtable.table):
        # i = index row
        # row value
        qi_sequence = csvtable._get_values(row, qi_names, i)  # list of values contained in qi_names at row 'i'

        # Skip if this row must be ignored:
        if qi_sequence is not None:
            qi_sequence = tuple(qi_sequence)  # list -> tuple ("val_a","val_b","val_c")

        if qi_sequence in qi_frequency:  # if qi_val_combination in qi_frequency Key
            occurrences = qi_frequency[qi_sequence][0] + 1  # add occurence of qi_sequence
            rows_set = qi_frequency[qi_sequence][1].union([i])  # add index
            qi_frequency[qi_sequence] = (occurrences, rows_set)  # update value
        else:
            # Initialize number of occurrences and set of row indices:
            qi_frequency[qi_sequence] = (1, set())
            qi_frequency[qi_sequence][1].add(i)
    #print("END gen_freq, qi_freq result: ",qi_frequency)
    return qi_frequency

#TODO: INPUT QUEUE FROM OUTSIDE
def mono_attr_verify(csvtable, graph, qi_names, qi_heights, k, dghs, k_anon_queue):

    #print("Enter Mono\n")
    #print("current k:",k)

    # vertex text format "qi_name1 : lv1 ; qi_name2 : lv2 ;..."

    for i in range(len(qi_names)):
        #print("\nCurrent QI: ",qi_names[i])
        prev_kanon = False
        qi_frequency = generate_frequency(csvtable, [qi_names[i]])

        list_tmp = []
        for n in range(qi_heights[qi_names[i]]):
            list_tmp.append(n)

        graph.add_vertices([list_tmp],[qi_names[i]])
        graph.mono_add_linked_edge([qi_names[i]])

        for j in range(qi_heights[qi_names[i]]):
            #print("\nCurrent I : ",i,"; Current J : ",j)
            node = qi_names[i] + ":" + str(j)
            print("Current Vertex:",node)
            if not graph.has_node(node):
                #print("Vertex <",node,"> doesn't exist!")
                return

            if not graph.isRoot(node):

                if graph.isMarked(list(graph.in_edges(node))[0][0]) and prev_kanon:
                    #print("[",node,"] INHERIT: ADDED to K_Anon")
                    graph.setMark(node)
                    prev_kanon = False
                    if k_anon_queue.get(1): #"None" is counted as "False"
                        k_anon_queue[1].append(node)
                    else:
                        k_anon_queue[1] = [node]
                elif is_k_anon(generalize([qi_names[i]], dghs, qi_frequency, *(j,)), k):
                    #print("[",node,"] ADDED to K_Anon")
                    graph.setMark(node)
                    prev_kanon = True
                    if k_anon_queue.get(1): #"None" is counted as "False"
                        k_anon_queue[1].append(node)
                    else:
                        k_anon_queue[1] = [node]
                    # add to input queue
            else:
                #If ROOT there's no parents to check
                if is_k_anon(generalize([qi_names[i]], dghs, qi_frequency, *(j,)), k):
                    #print("[",node,"] ADDED to K_Anon")
                    graph.setMark(node)
                    prev_kanon = True
                    if k_anon_queue.get(1): #"None" is counted as "False"
                        k_anon_queue[1].append(node)
                    else:
                        k_anon_queue[1] = [node]
                    # add to input queue
    #print("End k_anon_queue: ",k_anon_queue,"\n")
    #graph.printOut()
    return

# TODO: Verify which steps and functions are needed in order to achieve this funtion
def multi_attr_verify(qi_names, qi_heights, k, atr, dghs, qi_frequency, data):
    return


#TODO: CHANGE DIMENSION OF QI_NAMES TO CHECK SINGLE ATTRIBUTE
#data contains the generalization levels -> combination to generalize to
def generalize(qi_names, dghs, og_frequency, *data):
    #print("\nEnter Gen")
    #print("Current <COMB>: ", data)

    if all(n == 0 for n in data):
        return copy.copy(og_frequency)

    qi_frequency = copy.copy(og_frequency) #shallow copy

    # Look up table for the generalized values, to avoid searching in hierarchies:
    generalizations = dict()
    # Generalized value to apply for the needed lables
    generalized_value = dict()
    # Note: using the list of keys since the dictionary is changed in size at runtime
    # and it can't be used as an iterator:
    for j, qi_sequence in enumerate(list(qi_frequency)):
        #print("Current J: ",j)
        if j == 0: continue
        # Get the generalized value:
        for i in range(len(data)):
            # If QI is going back to genLv 0 then do nothing since it has already been "rolled back" with resetState
            # If old and new level are the same then do nothing once again
            #print(data[i])
            if data[i] != 0:
                if qi_sequence[i] in generalizations:
                    # Find directly the generalized value in the look up table:
                    generalized_value[i] = generalizations[i]
                else:
                    # Get the corresponding generalized value from the attribute DGH:
                    try:
                        #print("Enter Generalized_Jump")
                        #print("Current i: ", i, "; Current qi_names[i]", qi_names[i])
                        #print("data: ",data)
                        #print("qi_names: ",qi_names)
                        #print("Current i: ", i)
                        #print("qi_sequence[i] = ",qi_sequence[i])
                        generalized_value[i] = dghs[qi_names[i]] \
                            .generalize_jump(
                            qi_sequence[i], 0,
                            data[i])
                        #print("Exit Generalized_Jump")
                    except KeyError as error:
                        #print("Error: ",error)
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

    #print("Res qi_frequency: ",qi_frequency)
    return qi_frequency


if __name__ == "__main__":

    dgh_paths = dict()

    table_path = "/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/db_200.csv"

    k = 2

    qis = ("age", "sex", "zip_code")

    gen_paths = list()
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/age_generalization.csv")
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/sex_generalization.csv")
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/zip_code_generalization.csv")

    for i, qi_name in enumerate(qis):
        dgh_paths[qi_name] = gen_paths[i]
    table = CsvTable(table_path, dgh_paths)

    try:
        table.anonymize(qis, k)
    except KeyError as error:
        if len(error.args) > 0:
            print("[ERROR] Quasi Identifier", error.args[0], "is not valid.")
        else:
            print("[ERROR] A Quasi Identifier is not valid.")
    '''try:
        res = table.anonymize(qis, k)
    except KeyError as error:
        if len(error.args) > 0:
            print("[ERROR] Quasi Identifier",error.args[0],"is not valid.")
        else:
            print("[ERROR] A Quasi Identifier is not valid.")

    #print(datafly.is_k_anon(res, k))
    #print(datafly.suppress_under_k(res,k))

    for key in res:
        print("Key: ",key,"; Reps: ",res[key][0],", Set of rows: ", res[key][1])'''


    '''qi_heights = list()

    #CsvDGH.getTreeHeight(table.dghs[qis[0]])

    print(CsvDGH.get_tree_height(table.dghs[qis[0]]))

    #print(table.dghs[qis[0]].hierarchies['0-50'].root.children['0-20'].children['0-10'].children['1'].children)

    heights = list()
    for i in qis:
        tmp = list()
        for n in range(CsvDGH.get_tree_height(table.dghs[i])+1):
            tmp.append(n)
        qi_heights.append(tmp)

    print(qi_heights)

    #qi_heights = [[0, 1, 2, 3], [0, 1], [0, 1, 2, 3, 4, 5]]

    # create QI_Combination list to follow
    combinations = datafly.combination(*qi_heights)

    print(combinations)
'''