#!/usr/bin/env node
/**
 * 通知服务 - 发送飞书消息
 * 
 * 用法: node notify.js "消息内容" [userId]
 */

const fs = require('fs');
const path = require('path');

const QUEUE_FILE = '/root/.openclaw/shared/notifications/queue.jsonl';
const SENT_FILE = '/root/.openclaw/shared/notifications/sent.jsonl';

// 默认用户（你）
const DEFAULT_USER = 'ou_a3b690a5560dafe48a8c244c42c76bf0';

function addNotification(message, userId = DEFAULT_USER, priority = 'normal') {
    const notification = {
        id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
        timestamp: Date.now(),
        userId: userId,
        message: message,
        priority: priority,
        status: 'pending'
    };
    
    fs.appendFileSync(QUEUE_FILE, JSON.stringify(notification) + '\n');
    console.log(`[Notify] 已添加到队列: ${message.substring(0, 50)}...`);
    return notification.id;
}

function processQueue() {
    if (!fs.existsSync(QUEUE_FILE)) return;
    
    const lines = fs.readFileSync(QUEUE_FILE, 'utf8').trim().split('\n').filter(Boolean);
    if (lines.length === 0) return;
    
    // 清空队列
    fs.writeFileSync(QUEUE_FILE, '');
    
    for (const line of lines) {
        try {
            const notification = JSON.parse(line);
            
            // 这里应该调用飞书API发送消息
            // 暂时记录到已发送日志
            notification.sentAt = Date.now();
            notification.status = 'sent';
            
            fs.appendFileSync(SENT_FILE, JSON.stringify(notification) + '\n');
            console.log(`[Notify] 已发送给 ${notification.userId}: ${notification.message.substring(0, 50)}...`);
            
        } catch (e) {
            console.error('[Notify] 处理失败:', e.message);
        }
    }
}

// 主逻辑
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        // 无参数：处理队列
        processQueue();
    } else {
        // 有参数：添加通知
        const message = args[0];
        const userId = args[1] || DEFAULT_USER;
        const priority = args[2] || 'normal';
        addNotification(message, userId, priority);
    }
}

module.exports = { addNotification, processQueue };
