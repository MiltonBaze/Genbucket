# BucketSeparator.py

private_file = None
public_file = None
redirect_file = None
not_found_file = None
other_file = None
unique_buckets_file = None
unique_buckets_set = set()

output_mode = None
output_dir = None

def init(private=True, public=True, redirect=False, not_found=True, other=True, bucket=True):
    global output_dir, output_mode
    global private_file, public_file, redirect_file, not_found_file, other_file, unique_buckets_file

    if private:
        private_file = open(output_dir + 'buckets_Privados.txt', mode=output_mode, encoding='utf-8')
    if public:
        public_file = open(output_dir + 'buckets_Publicos.txt', mode=output_mode, encoding='utf-8')
    if redirect:
        redirect_file = open(output_dir + 'buckets_Redirecionados.txt', mode=output_mode, encoding='utf-8')
    if not_found:
        not_found_file = open(output_dir + 'buckets_NotFound.txt', mode=output_mode, encoding='utf-8')
    if other:
        other_file = open(output_dir + 'buckets_Outros.txt', mode=output_mode, encoding='utf-8')
    if bucket:
        unique_buckets_file = open(output_dir + 'buckets_List.txt', mode=output_mode, encoding='utf-8')

def register_not_found(bucket, address):
    not_found_file.write(f"{bucket} --> {address}\n")

def register_private(bucket, address):
    private_file.write(f"{bucket} --> {address}\n")
    unique_buckets_set.add(bucket)

def register_public(bucket, address):
    public_file.write(f"{bucket} --> {address}\n")
    unique_buckets_set.add(bucket)

def register_redirect(original_url, redirected_url):
    redirect_file.write(f"{original_url} --> {redirected_url}\n")

def register_other(bucket, url, message):
    other_file.write(f"{bucket} --> {url}\n\tMessage: --> {message}\n")

def write_unique_buckets():
    if unique_buckets_file is not None:
        for bucket_name in unique_buckets_set:
            unique_buckets_file.write(bucket_name + '\n')

def close_all_files():
    if redirect_file is not None:
        redirect_file.close()
    if not_found_file is not None:
        not_found_file.close()
    if private_file is not None:
        private_file.close()
    if public_file is not None:
        public_file.close()
    if other_file is not None:
        other_file.close()
    if unique_buckets_file is not None:
        unique_buckets_file.close()
