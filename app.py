# [Previous imports and setup unchanged]

@app.route('/privacy', methods=['GET'])
@login_required
def privacy():
    """
    Render privacy settings page with consent management and GDPR options.
    
    Returns:
        Response: Rendered HTML template with role-specific messages
    """
    return render_template('privacy.html', user=current_user, token=session.get('token'), user_id=session.get('user_id'), error=None, success_message=None)

@app.route('/api/privacy/anonymize', methods=['POST'])
@login_required
def anonymize_user_data():
    """
    Proxy anonymization request to backend with role-specific messages.
    
    Returns:
        Response: JSON response with role-specific messages
    """
    try:
        resp = requests.post(
            f'{BACKEND_URL}/patients/anonymize/{session["user_id"]}',
            headers={'Authorization': f'Bearer {session["token"]}', 'X-CSRF-Token': request.headers.get('X-CSRF-Token', os.getenv('CSRF_TOKEN', 'default-csrf-token'))}
        )
        resp.raise_for_status()
        data = resp.json()
        message = get_role_message(current_user.role, "data anonymization", True)
        data['message'] = message
        return jsonify(data), resp.status_code
    except Exception as e:
        logger.error(f"Anonymization proxy error: {e}")
        message = get_role_message(current_user.role, "data anonymization", False)
        return jsonify({'error': message}), 500

@app.route('/api/privacy/forget', methods=['DELETE'])
@login_required
def forget_user_data():
    """
    Proxy erasure request to backend with role-specific messages.
    
    Returns:
        Response: JSON response with role-specific messages
    """
    try:
        resp = requests.delete(
            f'{BACKEND_URL}/patients/forget/{session["user_id"]}',
            headers={'Authorization': f'Bearer {session["token"]}', 'X-CSRF-Token': request.headers.get('X-CSRF-Token', os.getenv('CSRF_TOKEN', 'default-csrf-token'))}
        )
        resp.raise_for_status()
        data = resp.json()
        message = get_role_message(current_user.role, "data erasure", True)
        data['message'] = message
        return jsonify(data), resp.status_code
    except Exception as e:
        logger.error(f"Erasure proxy error: {e}")
        message = get_role_message(current_user.role, "data erasure", False)
        return jsonify({'error': message}), 500

# New Template: templates/privacy.html
@app.route('/privacy')
@login_required
def privacy():
    return render_template('privacy.html', user=current_user, token=session.get('token'), user_id=session.get('user_id'))