from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Survey, Question, Choice, Answer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add(User(username="管理者", email="admin@example.com"))
        db.session.commit()

@app.route('/')
def index():
    surveys = Survey.query.all()
    return render_template('index.html', surveys=surveys)

@app.route('/create', methods=['GET', 'POST'])
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        new_survey = Survey(title=title, creator_id=1)
        db.session.add(new_survey)
        db.session.commit()
        return redirect(url_for('add_question', survey_id=new_survey.id))
    return render_template('create.html')

@app.route('/survey/<int:survey_id>/add_question', methods=['GET', 'POST'])
def add_question(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == 'POST':
        q_text = request.form.get('question_text')
        new_q = Question(text=q_text, survey_id=survey_id)
        db.session.add(new_q)
        db.session.flush()
        choices = request.form.getlist('choices')
        for c_text in choices:
            if c_text.strip():
                db.session.add(Choice(text=c_text, question_id=new_q.id))
        db.session.commit()
        if 'add_more' in request.form:
            return redirect(url_for('add_question', survey_id=survey_id))
        return redirect(url_for('index'))
    return render_template('add_question.html', survey=survey)

@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def survey_detail(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == 'POST':
        for q in survey.questions:
            choice_id = request.form.get(f'question_{q.id}')
            if choice_id:
                db.session.add(Answer(user_id=1, question_id=q.id, choice_id=choice_id))
        db.session.commit()
        return redirect(url_for('results', survey_id=survey_id))
    return render_template('survey.html', survey=survey)

@app.route('/results/<int:survey_id>')
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    report = []
    for q in survey.questions:
        q_data = {'question': q.text, 'results': []}
        for c in q.choices:
            count = Answer.query.filter_by(choice_id=c.id).count()
            q_data['results'].append({'choice': c.text, 'count': count})
        report.append(q_data)
    return render_template('results.html', survey=survey, report=report)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # すでに登録されているかチェック
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # 既にいる場合は、そのままトップへ（またはメッセージを出す）
            return redirect(url_for('index'))
        
        # 新規登録処理
        try:
            new_user = User(username=username, email=email)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return "登録中にエラーが発生しました。"
            
        return redirect(url_for('index'))
    return render_template('register.html')
# --- 削除機能の追加 ---
@app.route('/delete/<int:survey_id>', methods=['POST'])
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)

