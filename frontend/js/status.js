/**
 * 状态管理器
 * 管理小龙虾的三种状态：typing, waiting, thinking
 */

class StatusManager {
    constructor() {
        this.currentStatus = 'thinking';
        this.gifPaths = {
            typing: 'assets/gifs/typing.svg',
            waiting: 'assets/gifs/waiting.svg',
            thinking: 'assets/gifs/thinking.svg'
        };
        this.statusTexts = {
            typing: '输入中',
            waiting: '等待中',
            thinking: '思考中'
        };
        this.gifElement = null;
        this.indicatorDot = null;
        this.indicatorText = null;
        
        this.init();
    }

    init() {
        this.gifElement = document.getElementById('crab-status-gif');
        this.indicatorDot = document.querySelector('.indicator-dot');
        this.indicatorText = document.querySelector('.indicator-text');
        
        if (!this.gifElement) {
            console.warn('Status GIF element not found');
            return;
        }
        
        // 初始状态
        this.setStatus('thinking');
    }

    /**
     * 设置状态
     * @param {string} status - 'typing' | 'waiting' | 'thinking'
     */
    setStatus(status) {
        if (!['typing', 'waiting', 'thinking'].includes(status)) {
            console.error('Invalid status:', status);
            return;
        }

        if (this.currentStatus === status) {
            return;
        }

        console.log(`[StatusManager] 状态切换：${this.currentStatus} -> ${status}`);
        this.currentStatus = status;
        this.updateUI();
    }

    /**
     * 更新 UI 显示
     */
    updateUI() {
        if (!this.gifElement) return;

        // 淡出效果
        this.gifElement.classList.add('fade-out');

        setTimeout(() => {
            // 切换 GIF
            this.gifElement.src = this.gifPaths[this.currentStatus];
            
            // 更新状态指示器
            this.updateIndicator();
            
            // 淡入效果
            this.gifElement.classList.remove('fade-out');
            this.gifElement.classList.add('fade-in');
            
            setTimeout(() => {
                this.gifElement.classList.remove('fade-in');
            }, 300);
        }, 300);
    }

    /**
     * 更新状态指示器
     */
    updateIndicator() {
        if (this.indicatorDot && this.indicatorText) {
            // 移除所有状态类
            this.indicatorDot.classList.remove('typing', 'waiting', 'thinking');
            // 添加当前状态类
            this.indicatorDot.classList.add(this.currentStatus);
            // 更新文字
            this.indicatorText.textContent = this.statusTexts[this.currentStatus];
        }
    }

    /**
     * 获取当前状态
     * @returns {string}
     */
    getStatus() {
        return this.currentStatus;
    }

    /**
     * 设置 GIF 路径（用于自定义）
     * @param {string} status 
     * @param {string} path 
     */
    setGifPath(status, path) {
        if (this.gifPaths[status]) {
            this.gifPaths[status] = path;
        }
    }
}

// 导出为全局变量
window.StatusManager = StatusManager;
