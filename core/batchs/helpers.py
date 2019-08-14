import json
from django.utils.text import slugify


def uploads_directory_path(instance, filename):
    import time

    user_id = instance.User_ID.id
    timestamp = int(time.time())
    cleaned_file_name = slugify(filename)

    local_file_name = 'user_{0}/{1}-{2}'.format(user_id, timestamp, cleaned_file_name)

    return local_file_name


def convert_xls_to_csv(file_xls, file_csv):
    import xlrd
    import csv

    wb = xlrd.open_workbook(file_xls)

    for sheet_name in wb.sheet_names():
        sh = wb.sheet_by_name(sheet_name)

        with open(file_csv, 'w', encoding='utf-8') as dst:
            writer = csv.writer(dst, delimiter='\t')

            for rownum in range(sh.nrows):
                writer.writerow(sh.row_values(rownum))

        break # first worksheet only


def convert_csv_to_csv(src, file_csv):
    import csv

    with open(src, encoding='utf-8') as fin:
        dialect = csv.Sniffer().sniff(fin.read(1024))
        fin.seek(0)
        reader = csv.reader(fin, dialect)

        with open(file_csv, 'w', encoding='utf-8') as dst:
            writer = csv.writer(dst, delimiter='\t')

            for row in reader:
                writer.writerow(row)


def get_db_connection():
    from django.db import connections
    from django.conf import settings
    import sqlalchemy

    engine = sqlalchemy.create_engine(settings.DATABASE_ENGINE)
    con = engine.connect()
    return con


def load_csv(infile):
    import pandas as pd

    if infile.endswith('csv'):
        return pd.read_csv(infile, sep='[|,;\t]', engine='python', low_memory = True)

    elif infile.endswith('xls') or infile.endswith('xlsx'):
        return pd.read_excel(infile)

    else:
        raise Exception("unsupported file: expect csv, xls, xlsx")


def get_batch_input_table_name(batch_id):
    return "BATCH_INPUT_{}".format(batch_id)


def upload_to_mysql(df, table):
    con = get_db_connection()
    df.to_sql(con=con, name=table, if_exists='replace')
    con.close()


def handle_uploaded_file(local_file_name, batch, batch_id):
    df = load_csv(local_file_name)
    table = get_batch_input_table_name(batch_id)
    upload_to_mysql(df, table)
    pre_analyse(local_file_name, batch)


def pre_analyse(local_file_name, batch):
    import json
    from . import data_pre_analyser

    file_csv = local_file_name + ".csv"
    convert_uploaded_to_csv(local_file_name, file_csv)

    table_name = "BATCH_INPUT_{}".format(batch.Batch_Id)

    # Analyse with external analyser
    A = data_pre_analyser.analyse_source_data_find_input_output(
        file_csv, sql_mode=True, table_name=table_name, con=get_db_connection())
    batch.AnalysisSource_ColumnsNameInput           = A.column_names_input
    batch.AnalysisSource_ColumnsNameOutput          = A.column_names_output
    batch.AnalysisSource_ColumnType                 = A.column_types
    batch.AnalysisSource_CountLinesForTraining      = A.lines_for_training_count
    batch.AnalysisSource_CountLinesForPrediction    = A.lines_to_predict_count
    batch.AnalysisSource_Errors                     = A.errors_info
    batch.AnalysisSource_Warnings                   = A.warning_info


def convert_uploaded_to_csv(local_file_name, file_csv):
    # convert
    if local_file_name.endswith("xls"):
        convert_xls_to_csv(local_file_name, file_csv)

    elif local_file_name.endswith("xlsx"):
        convert_xls_to_csv(local_file_name, file_csv)

    elif local_file_name.endswith("csv"):
        convert_csv_to_csv(local_file_name, file_csv)

    else:
        raise Exception("unsupported file type. expected csv, xls, xlsx") # FAIL


def get_csv_lines(file_name, first_lines, last_lines):
    title = []
    first = []
    last  = []

    import csv
    with open(file_name, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            title = row
            break # one only

        reader = csv.reader(csvfile, delimiter='\t')

        # head
        for i, row in enumerate(reader):
            if i < first_lines:
                first.append(row)
            else:
                break

        # tail
        # check tail
        for i, row in enumerate(reader):
            if i < last_lines:
                last.append(row)
            else:
                break

        # check block length
        if len(last) <= last_lines:
            # small file. All reads
            pass
        else:
            # big file. Need read tail
            last = []
            tail_reader = csv.reader(FileTail(file_name), delimiter='\t')

            for i, row in enumerate(tail_reader):
                if i < last_lines:
                    last.append(row)
                else:
                    break

    return (title, first, last)


class FileTail(object):
    """
    Tail a file, even if its rotated/truncated.
    Inspiration came from the perl module File::Tail.
    """
    import time
    import os

    def __init__(self,
                 file,  # filename to monitor
                 start_pos="end",  # where to initially start reading from
                 # max_buffer_size=16384, # Max buffer size hint (Not exact; @see file.readlines)
                 interval=0.1,  # sleep time to wait if no data is present (dynamically changes)
                 # min_interval=0.01,     # min sleep time
                 max_interval=5,  # max sleep time
                 max_wait=60,  # max time to wait with no data before reopening file
                 reopen_check="inode",
                 # how to check if file is different (inode or time) - inode does not work on win32
                 encoding="utf-8"  # file encoding
                 ):

        self.start_pos = start_pos
        self.reopen_check = reopen_check
        self.max_wait = max_wait
        # self.max_buffer_size = max_buffer_size
        # self.min_interval = min_interval
        self.max_interval = max_interval
        self.interval = interval
        if self.interval > self.max_interval:
            self.interval = self.max_interval
        self.encoding = encoding

        # will throw exception if it fails... caller should intercept
        self.open(file, start_pos=start_pos)

        # initialize some internal vars
        self._buffer = []
        self.last_time = time()
        self.last_count = 0

    def open(self, file, start_pos="head"):
        """Open the file to tail and initialize our state."""
        fh = open(file, "r", encoding=self.encoding)

        # seek to the initial position in the file we want to start reading
        if start_pos == "end" or start_pos == "tail":
            fh.seek(0, os.SEEK_END)  # End of file
        elif start_pos == "start" or start_pos == "head":
            # fh.seek(0, os.SEEK_SET)                      # Beginning of file
            pass
        elif start_pos is not None:
            if start_pos >= 0:  # Absolute position
                fh.seek(start_pos, os.SEEK_SET)
            else:  # Absolute position (from end)
                fh.seek(abs(start_pos), os.SEEK_END)

        # if we passed the end of the file rewind to the actual end.
        # This avoids a potential race condition if the file was being rotated
        # in the process of opening the file. Not sure if this can actually
        # happen, but better safe than sorry.
        pos = fh.tell()
        if pos > os.stat(file)[ST_SIZE]:
            pos = fh.tell()

        self.fh = fh
        self.pos = pos
        self.stat = os.fstat(fh.fileno())
        self.file = file

    def reopen(self):
        """
        Attempt to reopen the current file. If it doesn't appear to have
        changed (been rotated) then the current file handle is not changed.
        """

        # print("Reopening", self.file, "...", end="")

        # if we don't have an opened file already then try to open it now
        if not self.fh or self.fh.closed:
            try:
                self.open(self.file, start_pos="head");
            except IOError:
                return False
            return True

        # save current values
        fh = self.fh
        pos = self.pos
        cur = self.stat

        # reopen same file
        try:
            self.open(self.file, "head")
        except IOError as e:
            # print("FILE DOES NOT EXIST")
            return False

        new = self.stat
        # print(new.st_ino, ' == ', cur.st_ino)
        if (
                (self.reopen_check == 'inode' and new.st_ino == cur.st_ino)
                or
                (self.reopen_check == 'time' and new.st_mtime <= floor(self.last_time) and new.st_size == pos)
        ):
            # print("FILE NOT CHANGED")
            # file appears to be the same or older than our last read
            # self.last_time = new.st_mtime
            self.fh = fh
            self.pos = pos
            self.stat = cur
            return False

        # print("NEW FILE")
        return True

    def __iter__(self):
        """
            Return iterator to support:
                for line in filetail:
                    print line
        """
        self.wait_count = 0
        return self

    def __next__(self):
        """Interator "next" call."""
        return self.next()

    def next(self):
        line = None
        self.wait_count = 0

        # low CPU (probably same as the block below this, but ALLOWS tell()!
        while not line:
            line = self.fh.readline()
            if line != "":
                # track the time we received new data and how much
                self.last_time = time()
                self.last_count = 1
            else:
                self.wait()

        return line


def from_json(s, default=None):
    if s:
        return json.loads(s)
    else:
        return default


def to_json(s):
    if s is None:
        return None
    else:
        return json.dumps(s)


def get_all_fields_from_form(instance):
    """"
    Return names of all available fields from given Form instance.

    :arg instance: Form instance
    :returns list of field names
    :rtype: list
    """

    fields = list(instance().base_fields)

    for field in list(instance().declared_fields):
        if field not in fields:
            fields.append(field)
    return fields
