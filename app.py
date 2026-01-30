from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Survey, Question, Choice, Answer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# データベースの初期化
with app.app_context():
    db.create_all()
    # テスト用ユーザーの作成（本来は登録画面から作成）
    if not User.query.first():
        sample_user = User(username="Admin", email="admin@example.com")
        db.session.add(sample_user)
        db.session.commit()

@app.route('/')
def index():
    surveys = Survey.query.all()
    return render_template('index.html', surveys=surveys)

@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def survey_detail(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == 'POST':
        # 回答の保存ロジック
        for question in survey.questions:
            choice_id = request.form.get(f'question_{question.id}')
            if choice_id:
                answer = Answer(user_id=1, question_id=question.id, choice_id=choice_id)
                db.session.add(answer)
        db.session.commit()
        return redirect(url_for('results', survey_id=survey_id))
    
    return render_template('survey.html', survey=survey)

@app.route('/results/<int:survey_id>')
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    report = []
    for q in survey.questions:
        q_data = {'question': q.text, 'results': []}
        for choice in q.choices:
            count = Answer.query.filter_by(choice_id=choice.id).count()
            q_data['results'].append({'choice': choice.text, 'count': count})
        report.append(q_data)
    return render_template('results.html', survey=survey, report=report)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/create', methods=['GET', 'POST'])
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        # ユーザーIDはとりあえず1（管理者）で固定
        new_survey = Survey(title=title, creator_id=1)
        db.session.add(new_survey)
        db.session.commit()
        # 作成したアンケートに質問を追加する画面へ
        return redirect(url_for('add_question', survey_id=new_survey.id))
    return render_template('create.html')

@app.route('/survey/<int:survey_id>/add_question', methods=['GET', 'POST'])
def add_question(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == 'POST':
        # 質問の保存
        q_text = request.form.get('question_text')
        new_q = Question(text=q_text, survey_id=survey_id)
        db.session.add(new_q)
        db.session.flush() # ID確定のために一度流す

        # 選択肢の保存（空文字以外を登録）
        choices = request.form.getlist('choices')
        for c_text in choices:
            if c_text.strip():
                new_choice = Choice(text=c_text, question_id=new_q.id)
                db.session.add(new_choice)
        
        db.session.commit()
        
        # 「さらに質問を追加」か「完了して一覧へ」か
        if 'add_more' in request.form:
            return redirect(url_for('add_question', survey_id=survey_id))
        return redirect(url_for('index'))

    return render_template('add_question.html', survey=survey)