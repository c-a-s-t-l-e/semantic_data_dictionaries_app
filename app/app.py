from shiny import App, reactive, render, ui
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import csv

group_styles = """
.table-groups {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
}
.table-groups thead th {
    background-color: #f8f9fa;
    font-weight: bold;
    border: 1px solid #ddd;
    padding: 8px;
}
.table-groups tbody td {
    border: 1px solid #ddd;
    padding: 8px;
}
.table-groups tbody tr.group-1 td { background-color: rgba(255, 223, 223, 0.9); }
.table-groups tbody tr.group-2 td { background-color: rgba(223, 255, 223, 0.9); }
.table-groups tbody tr.group-3 td { background-color: rgba(223, 223, 255, 0.9); }
.table-groups tbody tr.group-4 td { background-color: rgba(255, 255, 223, 0.9); }
.table-groups tbody tr.group-5 td { background-color: rgba(255, 223, 255, 0.9); }
.table-groups tbody tr.group-6 td { background-color: rgba(223, 255, 255, 0.9); }
.table-groups tbody tr.group-7 td { background-color: rgba(255, 240, 223, 0.9); }
.table-groups tbody tr.group-8 td { background-color: rgba(240, 223, 255, 0.9); }
.table-groups tbody tr.group-9 td { background-color: rgba(223, 255, 240, 0.9); }
.table-groups tbody tr.group-10 td { background-color: rgba(255, 223, 240, 0.9); }
"""

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style(group_styles)
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Settings"),
            ui.input_file(
                "files",
                "Upload CSV files",
                accept=[".csv"],
                multiple=True
            ),
            ui.input_numeric("min_similarity", "Minimum Similarity Score (0-1)", 
                           value=0.3, min=0, max=1, step=0.05),
            ui.h4("Column Mappings"),
            ui.output_ui("column_selectors"),
            width="300px"
        ),
        ui.card(
            ui.h4("Uploaded Files"),
            ui.output_table("uploaded_files"),
        ),
        ui.card(
            ui.h4("Similar Column Groups"),
            ui.output_ui("similar_groups"),
        ),
    )
)

def server(input, output, session):
    vectorizer = reactive.value(None)
    file_columns = reactive.value({})
    file_id_mapping = reactive.value({})
    
    def sanitize_id(filename):
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
        if not sanitized[0].isalpha():
            sanitized = 'f' + sanitized
        return sanitized
    
    @reactive.effect
    def _():
        if vectorizer() is None:
            vectorizer.set(TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9
            ))

    @reactive.effect
    def _update_file_columns():
        files_info = input.files()
        if files_info:
            new_columns = {}
            new_mapping = {}
            for file_info in files_info:
                try:
                    try:
                        df = pd.read_csv(file_info['datapath'])
                    except pd.errors.ParserError:
                        try:
                            df = pd.read_csv(file_info['datapath'], quotechar='"', escapechar='\\')
                        except pd.errors.ParserError:
                            df = pd.read_csv(file_info['datapath'], quoting=csv.QUOTE_NONE)
                    
                    filename = file_info['name']
                    new_columns[filename] = list(df.columns)
                    new_mapping[filename] = sanitize_id(filename)
                except Exception as e:
                    print(f"Error reading file {file_info['name']}: {str(e)}")
                    continue
            file_columns.set(new_columns)
            file_id_mapping.set(new_mapping)

    @render.ui
    def column_selectors():
        files_info = input.files()
        if not files_info:
            return ui.div()
        
        selectors = []
        columns = file_columns()
        id_mapping = file_id_mapping()
        
        for file_info in files_info:
            filename = file_info['name']
            if filename in columns and filename in id_mapping:
                file_id = id_mapping[filename]
                selectors.extend([
                    ui.h5(filename),
                    ui.input_select(
                        f"colname_{file_id}",
                        "Column Name Column",
                        choices=columns[filename]
                    ),
                    ui.input_select(
                        f"coldesc_{file_id}",
                        "Description Column",
                        choices=columns[filename]
                    ),
                    ui.tags.hr()
                ])
        
        return ui.div(selectors)

    @render.table
    def uploaded_files():
        files_info = input.files()
        if not files_info or len(files_info) == 0:
            return pd.DataFrame({"Message": ["No files uploaded yet"]})
        
        file_list = []
        for file_info in files_info:
            try:
                try:
                    df = pd.read_csv(file_info['datapath'])
                except pd.errors.ParserError:
                    try:
                        df = pd.read_csv(file_info['datapath'], quotechar='"', escapechar='\\')
                    except pd.errors.ParserError:
                        df = pd.read_csv(file_info['datapath'], quoting=csv.QUOTE_NONE)
                
                file_list.append({
                    'Filename': file_info['name'],
                    'Number of Columns': len(df.columns),
                    'Status': 'Loaded successfully'
                })
            except Exception as e:
                file_list.append({
                    'Filename': file_info['name'],
                    'Number of Columns': 0,
                    'Status': f'Error: {str(e)}'
                })
        
        return pd.DataFrame(file_list)
    
    def process_similar_groups():
        files_info = input.files()
        if not files_info or len(files_info) == 0:
            return None
        
        all_columns = []
        all_descriptions = []
        sources = []
        
        id_mapping = file_id_mapping()
        
        for file_info in files_info:
            try:
                filename = file_info['name']
                if filename not in id_mapping:
                    continue
                    
                file_id = id_mapping[filename]
                
                try:
                    df = pd.read_csv(file_info['datapath'])
                except pd.errors.ParserError:
                    try:
                        df = pd.read_csv(file_info['datapath'], quotechar='"', escapechar='\\')
                    except pd.errors.ParserError:
                        df = pd.read_csv(file_info['datapath'], quoting=csv.QUOTE_NONE)
                
                col_name = getattr(input, f"colname_{file_id}")()
                col_desc = getattr(input, f"coldesc_{file_id}")()
                
                if not col_name or not col_desc:
                    continue
                
                columns = df[col_name]
                descriptions = df[col_desc]
                
                all_columns.extend(columns)
                all_descriptions.extend(descriptions)
                sources.extend([filename] * len(columns))
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue
        
        if not all_columns:
            return None
            
        texts = [f"{col.lower()} {desc.lower()}" for col, desc in zip(all_columns, all_descriptions)]
        
        embeddings = vectorizer().fit_transform(texts)
        similarity_matrix = cosine_similarity(embeddings)
        
        min_similarity = input.min_similarity()
        used_indices = set()
        
        total_similarities = similarity_matrix.sum(axis=1)
        sorted_indices = np.argsort(-total_similarities)
        
        result_rows = []
        current_group = 1
        
        for i in sorted_indices:
            if i in used_indices:
                continue
            
            similar_mask = similarity_matrix[i] >= min_similarity
            similar_indices = np.where(similar_mask)[0]
            similar_indices = [j for j in similar_indices if j not in used_indices]
            
            if len(similar_indices) > 0:
                result_rows.append({
                    'Group': str(current_group),
                    'group_num': current_group,
                    'Similarity': 1.0,
                    'Source': sources[i],
                    'Column Name': all_columns[i],
                    'Description': all_descriptions[i]
                })
                used_indices.add(i)
                
                for j in similar_indices:
                    if j != i:
                        result_rows.append({
                            'Group': str(current_group),
                            'group_num': current_group,
                            'Similarity': similarity_matrix[i][j],
                            'Source': sources[j],
                            'Column Name': all_columns[j],
                            'Description': all_descriptions[j]
                        })
                        used_indices.add(j)
                
                current_group += 1
        
        if not result_rows:
            return None
            
        df = pd.DataFrame(result_rows)
        df = df.sort_values(['group_num', 'Similarity'], ascending=[True, False])
        return df

    @render.ui
    def similar_groups():
        df = process_similar_groups()
        if df is None:
            return ui.HTML('<div class="alert alert-info">Please upload data dictionary files and select columns</div>')
    
        df = df.copy()
        # Convert similarity to numeric to ensure proper formatting
        df['Similarity'] = pd.to_numeric(df['Similarity'])
        # Format similarity as percentage with 1 decimal place
        df['Similarity'] = df['Similarity'].apply(lambda x: f"{x*100:.2f}")
    
        table_html = '<div style="overflow-x: auto;"><table class="table table-groups">'
        table_html += '<thead><tr><th>Group</th><th>Similarity</th><th>Source</th><th>Column Name</th><th>Description</th></tr></thead>'
        table_html += '<tbody>'
    
        for _, row in df.iterrows():
            group_num = row['group_num']
            color_class = f"group-{((group_num-1) % 10) + 1}"
            table_html += f'<tr class="{color_class}">'
            table_html += f'<td>{row["Group"]}</td>'
            table_html += f'<td>{row["Similarity"]}</td>'
            table_html += f'<td>{row["Source"]}</td>'
            table_html += f'<td>{row["Column Name"]}</td>'
            table_html += f'<td>{row["Description"]}</td>'
            table_html += '</tr>'
    
        table_html += '</tbody></table></div>'
        return ui.HTML(table_html)

app = App(app_ui, server)
