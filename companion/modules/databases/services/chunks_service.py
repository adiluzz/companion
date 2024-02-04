
def parse_chunk(chunk):
    prompt_eval_time = chunk.split('prompt eval time')[1]
    tokens = prompt_eval_time.split('tokens')[0].split('/')[1].replace(' ', '')
    ms_per_token = prompt_eval_time.split('tokens ( ')[1].split('ms')[0]
    chunk_total_time = prompt_eval_time.split('total time =')[1].split('ms')[0].replace(' ', '')
    response = {}
    response['ms_per_token'] = float(ms_per_token)
    response['tokens'] = int(tokens)
    response['chunk_total_time'] = float(chunk_total_time)
    return response


def get_chunks(path):
    with open(path) as file:
        file_data = file.read()
        splitter = 'load time'
        splitted = file_data.split(splitter)
        if len(splitted) > 1:
            chunks = []
            for idx, chunk in enumerate(splitted):
                if idx > 0:
                    parsed = parse_chunk(chunk=chunk)
                    chunks.append(parsed)
            return chunks
        else:
            return None

def get_average(list):
    return sum(list)/len(list)

def get_database_average_from_chunks(chunks):
    ms_per_token = []
    tokens = []
    chunk_total_times = []
    for chunk in chunks:
        tokens.append(chunk.tokens)
        ms_per_token.append(chunk.ms_per_token)
        chunk_total_times.append(chunk.chunk_total_time)
    response = {}
    response['average_tokens_per_chunk'] = get_average(tokens)
    response['average_ms_per_token'] = get_average(ms_per_token)
    response['average_chunk_total_time'] = get_average(chunk_total_times)
    return response
