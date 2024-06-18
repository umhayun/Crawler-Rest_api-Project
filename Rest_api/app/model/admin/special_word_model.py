from flask import current_app

def delete_specialword(es,data) :

    # 기존글 삭제 체크박스 추가 (politic/nation은 제목/댓글 삭제, not_comment는 댓글만 삭제, delete는 체크박스 없음)    
    word_type = data['type']
    terms = ["title", "comment"]
    word = data['word'].strip()
    if word_type != 'delete':
        if word_type == 'not_comment':
            terms = ['comment']
        result = es.delete_by_query(index = 'embedding-*',
                        body =  {
                                "query": {
                                "bool": {
                                    "must": [
                                    {
                                        "wildcard": {
                                            "text": {
                                                "value": f"*{word}*"
                                            }
                                        }
                                    },
                                    {
                                    "terms": {
                                        "type.keyword": terms
                                        }
                                    }
                                ]}
                                
                                }
                            })
    return result