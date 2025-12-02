# Add these routes to your app_min.py (or app.py)
# Copy and paste this section into your Flask app

# ============================================================================
# HaGOLEM IDEAS DATABASE ROUTES
# ============================================================================

# First, add this import at the top if not already there:
# import mysql.connector

# Database connection function (adjust credentials)
def get_hagolem_db():
    return mysql.connector.connect(
        host='your-mysql-host.mysql.pythonanywhere-services.com',
        user='your-username',
        password='your-password',
        database='your-database-name'
    )

@app.route('/hagolem')
def hagolem_dashboard():
    """HaGOLEM Ideas Dashboard"""
    return render_template('hagolem_ideas.html')

@app.route('/api/hagolem/stats')
def hagolem_stats():
    """Get statistics"""
    try:
        conn = get_hagolem_db()
        cursor = conn.cursor(dictionary=True)
        
        stats = {}
        cursor.execute("SELECT COUNT(*) as total FROM hagolem_ideas")
        stats['total'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT status, COUNT(*) as count FROM hagolem_ideas GROUP BY status")
        stats['by_status'] = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as count FROM hagolem_ideas WHERE date_created >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        stats['recent'] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hagolem/ideas', methods=['GET'])
def get_hagolem_ideas():
    """Get all ideas or filtered"""
    try:
        conn = get_hagolem_db()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM hagolem_ideas WHERE 1=1"
        params = []
        
        if request.args.get('type'):
            query += " AND idea_type = %s"
            params.append(request.args.get('type'))
        
        if request.args.get('category'):
            query += " AND category = %s"
            params.append(request.args.get('category'))
        
        if request.args.get('status'):
            query += " AND status = %s"
            params.append(request.args.get('status'))
        
        if request.args.get('search'):
            search = f"%{request.args.get('search')}%"
            query += " AND (idea_title LIKE %s OR idea_content LIKE %s OR tags LIKE %s)"
            params.extend([search, search, search])
        
        query += " ORDER BY date_created DESC"
        
        cursor.execute(query, params)
        ideas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(ideas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hagolem/ideas', methods=['POST'])
def add_hagolem_idea():
    """Add new idea"""
    try:
        data = request.json
        conn = get_hagolem_db()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO hagolem_ideas 
            (idea_title, idea_content, idea_type, category, priority, status, tags, source_file)
            VALUES (%s, %s, %s, %s, %s, 'New', %s, %s)
        """
        
        values = (
            data.get('title'),
            data.get('content'),
            data.get('type'),
            data.get('category'),
            data.get('priority', 'Medium'),
            data.get('tags'),
            data.get('source_file')
        )
        
        cursor.execute(query, values)
        conn.commit()
        idea_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'id': idea_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hagolem/ideas/<int:idea_id>', methods=['PUT'])
def update_hagolem_idea(idea_id):
    """Update idea"""
    try:
        data = request.json
        conn = get_hagolem_db()
        cursor = conn.cursor()
        
        query = """
            UPDATE hagolem_ideas 
            SET idea_title = %s, idea_content = %s, idea_type = %s, 
                category = %s, priority = %s, tags = %s, source_file = %s
            WHERE id = %s
        """
        
        values = (
            data.get('title'),
         .   data.get('content'),
            data.get('type'),
            data.get('category'),
            data.get('priority'),
            data.get('tags'),
            data.get('source_file'),
            idea_id
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hagolem/ideas/<int:idea_id>', methods=['DELETE'])
def delete_hagolem_idea(idea_id):
    """Delete idea"""
    try:
        conn = get_hagolem_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM hagolem_ideas WHERE id = %s", (idea_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500