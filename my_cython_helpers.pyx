from math import ceil
import numpy

cdef int count_preferences_in_list(dict guest_lookup, int[:] guest_numbers, int preference_number, int start, int stop):
    cdef int count = 0, i, j
    cdef dict guest_preferences
    cdef int pref
    for i in range(start, stop):
        if guest_numbers[i] == -1:
            continue
        guest_preferences = guest_lookup[guest_numbers[i]]
        if guest_preferences is None or len(guest_preferences) == 0:
            continue
        for j in range(start, stop):
            if i == j:
                continue
            if guest_numbers[j] == -1:
                continue
            try:
                pref = guest_preferences[guest_numbers[j]]
            except (KeyError):
                continue
            if pref == preference_number:
                count += 1
    return count


cdef int count_dislikes_in_list(dict guest_lookup, int[:] guest_numbers, int start, int stop):
    return count_preferences_in_list(guest_lookup, guest_numbers, 0, start, stop)


cdef int count_likes_in_list(dict guest_lookup, int[:] guest_numbers, int start, int stop):
    return count_preferences_in_list(guest_lookup, guest_numbers, 1, start, stop)


# Seating chart evaluation
cpdef tuple evaluate(dict indiv_and_else):
    cdef int [:] individual = numpy.array(indiv_and_else['indiv'], dtype='intc')
    cdef int table_size = indiv_and_else['size']
    cdef dict guest_lookup = indiv_and_else['lookup']
    cdef int num_tables = int(ceil(len(individual) / table_size))
    cdef int dislike_score = 0
    cdef int like_score = 0
    cdef int t, start, stop
    for t in range(num_tables):
        dislike_score = dislike_score + count_dislikes_in_list(guest_lookup, individual, t*table_size, (t + 1)*table_size)
        like_score = like_score + count_likes_in_list(guest_lookup, individual, t*table_size, (t + 1)*table_size)
    return dislike_score, like_score