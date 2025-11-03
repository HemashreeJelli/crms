import oracledb
oracledb.init_oracle_client()


def insert_evidence_record(connection, case_id, evidence_type, description,
                           collected_by, storage_location, chain_of_custody, status):

    sql = """
        INSERT INTO evidence
        (case_id, evidence_type, description, collected_by, storage_location,
         chain_of_custody, status)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
        RETURNING evidence_id INTO :8
    """

    try:
        with connection.cursor() as cursor:
            evidence_id = cursor.var(int)
            cursor.execute(sql, (case_id, evidence_type, description, collected_by,
                                 storage_location, chain_of_custody, status, evidence_id))
            connection.commit()
            return evidence_id.getvalue()
    except Exception as e:
        raise Exception(f"Error inserting evidence record: {e}")


def insert_evidence_file(connection, evidence_id, filename, file_type, uploaded_by, description, file_path):

    with open(file_path, 'rb') as file:
        file_data = file.read()
        file_size = len(file_data)

    sql = """
        INSERT INTO evidence_file
        (evidence_id, filename, file_type, file_size, file_content, uploaded_by, description)
        VALUES (:evidence_id, :filename, :file_type, :file_size, :file_content, :uploaded_by, :description)
    """

    try:
        with connection.cursor() as cursor:

            cursor.setinputsizes(file_content=oracledb.DB_TYPE_BLOB)

            cursor.execute(sql, {
                "evidence_id": evidence_id,
                "filename": str(filename),
                "file_type": str(file_type),
                "file_size": file_size,
                "file_content": file_data,  # <-- raw bytes
                "uploaded_by": str(uploaded_by),
                "description": str(description)
            })

            connection.commit()
    except Exception as e:
        raise Exception(f"Error inserting evidence file: {e}")

