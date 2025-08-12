function generateJWTToken(userId) {
    // JWT 토큰 생성 API 호출
    fetch(`/admin/userapp/user/generate-jwt/${userId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 모달 창으로 토큰 정보 표시
        showTokenModal(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('JWT 토큰 생성 중 오류가 발생했습니다.');
    });
}

function showTokenModal(tokenData) {
    // 모달 HTML 생성
    const modalHtml = `
        <div id="jwt-token-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 8px;
                max-width: 800px;
                width: 90%;
                max-height: 80%;
                overflow-y: auto;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h2 style="margin-top: 0; color: #333;">JWT 토큰 정보</h2>
                <div style="margin-bottom: 20px;">
                    <h3>사용자 정보:</h3>
                    <p><strong>사용자 ID:</strong> ${tokenData.user_id}</p>
                    <p><strong>사용자명:</strong> ${tokenData.username}</p>
                    <p><strong>이메일:</strong> ${tokenData.email}</p>
                    <p><strong>식별자:</strong> ${tokenData.identifier}</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3>Access Token:</h3>
                    <textarea readonly style="
                        width: 100%;
                        height: 150px;
                        padding: 10px;
                        font-family: monospace;
                        font-size: 12px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background-color: #f8f9fa;
                        resize: vertical;
                    " onclick="this.select()">${tokenData.access_token}</textarea>
                    <button onclick="copyToClipboard('${tokenData.access_token}')" style="
                        margin-top: 5px;
                        padding: 5px 10px;
                        background-color: #007cba;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        cursor: pointer;
                    ">Access Token 복사</button>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3>Refresh Token:</h3>
                    <textarea readonly style="
                        width: 100%;
                        height: 150px;
                        padding: 10px;
                        font-family: monospace;
                        font-size: 12px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background-color: #f8f9fa;
                        resize: vertical;
                    " onclick="this.select()">${tokenData.refresh_token}</textarea>
                    <button onclick="copyToClipboard('${tokenData.refresh_token}')" style="
                        margin-top: 5px;
                        padding: 5px 10px;
                        background-color: #007cba;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        cursor: pointer;
                    ">Refresh Token 복사</button>
                </div>
                
                <div style="text-align: right;">
                    <button onclick="closeTokenModal()" style="
                        padding: 10px 20px;
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                    ">닫기</button>
                </div>
            </div>
        </div>
    `;
    
    // 모달을 body에 추가
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeTokenModal();
        }
    });
}

function closeTokenModal() {
    const modal = document.getElementById('jwt-token-modal');
    if (modal) {
        modal.remove();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // 임시 알림 표시
        const notification = document.createElement('div');
        notification.textContent = '클립보드에 복사되었습니다!';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            z-index: 10000;
            font-size: 14px;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }).catch(function(err) {
        console.error('클립보드 복사 실패:', err);
        alert('클립보드 복사에 실패했습니다.');
    });
}

// CSRF 토큰을 가져오는 헬퍼 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 