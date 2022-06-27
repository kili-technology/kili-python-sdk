def pluralize(word, count):
    """Transform a word to plural based on the given numeric value.
    Does not take into account the irregular words

    Args:
        word: the word to print
        count: the value associated to the word"""
    if count < 2:
        return word
    else:
        if word.endswith('y'):
            # If there is a vowel before y
            if word[-2:-1] in 'aeiou':
                return word + 's'
            # If not a vowel before y
            else:
                return word[:-1] + 'ies'
        # o, ch, s, sh, x, or z endings
        if (word.endswith('o') or
            word.endswith('ch') or
            word.endswith('s') or
            word.endswith('sh') or
                word.endswith('z')):
            return word + 'es'
        # general case
        else:
            return word + 's'


def print_final_log_create_prediction(nb_labels_uploaded: int, errors: dict, verbose: int):
    """Print final log when importing labels from the CLI

    X label sucessfully uploaded
    Y import errors:
            Y1 file not found
            Y2 json decode error

    Args:
        nb_labels_uploaded: number of labels sucessfully uploaded
        errors: dictionary with external_ids for which the label upload encountered an error,
            grouped by error: not_found_errors, json_decode_errors
        verbose: wether to show the error synthesis

    """
    print(f"{nb_labels_uploaded} {pluralize('label',nb_labels_uploaded)} sucessfully uploaded")
    nb_not_found_errors = len(errors['not_found_err ors'])
    nb_json_decode_errors = len(errors['json_decode_errors'])
    if verbose and nb_json_decode_errors+nb_not_found_errors > 0:
        print(f"{nb_json_decode_errors+nb_not_found_errors} import "
              f"{pluralize('error',nb_json_decode_errors+nb_not_found_errors)}:",
              end='\n\t')
        print(
            f"{nb_not_found_errors} {pluralize('file',nb_json_decode_errors)} not found",
            end='\n\t')
        print(
            f"{nb_json_decode_errors} json decode {pluralize('error',nb_not_found_errors)}")
