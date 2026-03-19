/**
 * 主应用入口
 * 初始化所有模块并启动应用
 */

// 全局应用实例
const app = {
    statusManager: null,
    videoStatusManager: null,  // 新增：视频状态管理器
    thoughtLogger: null,
    mindmapRenderer: null,
    mockAgent: null,
    
    /**
     * 初始化应用
     */
    init() {
        console.log('[App] 初始化 OpenClaw 直播网页...');
        
        // 1. 初始化视频状态管理器（优先）
        this.videoStatusManager = new VideoStatusManager();
        console.log('[App] 视频状态管理器已初始化');
        
        // 2. 初始化状态管理器（保留用于指示灯）
        this.statusManager = new StatusManager();
        console.log('[App] 状态管理器已初始化');
        
        // 3. 初始化思考日志
        this.thoughtLogger = new ThoughtLogger('logger-container');
        console.log('[App] 思考日志已初始化');
        
        // 4. 初始化思维导图
        this.mindmapRenderer = new MindmapRenderer('mindmap-container');
        console.log('[App] 思维导图已初始化');
        
        // 5. 初始化 Mock Agent
        this.mockAgent = new MockAgent(
            this.statusManager,
            this.thoughtLogger,
            this.mindmapRenderer
        );
        console.log('[App] Mock Agent 已初始化');
        
        // 6. 添加初始日志
        this.thoughtLogger.addLog('🎉 OpenClaw 直播系统启动！', 'success');
        this.thoughtLogger.addLog('🤖 Mock Agent 准备就绪', 'info');
        
        // 7. 启动 Mock Agent
        setTimeout(() => {
            this.mockAgent.start();
            this.thoughtLogger.addLog('▶️ 开始模拟工作流程...', 'info');
        }, 1000);
        
        console.log('[App] 应用初始化完成');
    },
    
    /**
     * 获取所有模块状态
     */
    getStatus() {
        return {
            statusManager: this.statusManager ? 'running' : 'not initialized',
            thoughtLogger: this.thoughtLogger ? 'running' : 'not initialized',
            mindmapRenderer: this.mindmapRenderer ? 'running' : 'not initialized',
            mockAgent: this.mockAgent ? (this.mockAgent.isRunning ? 'running' : 'stopped') : 'not initialized'
        };
    },
    
    /**
     * 停止应用
     */
    stop() {
        if (this.mockAgent) {
            this.mockAgent.stop();
        }
        if (this.mindmapRenderer) {
            this.mindmapRenderer.stopPolling();
        }
        console.log('[App] 应用已停止');
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    app.init();
    
    // 暴露到全局方便调试
    window.app = app;
});

// 页面关闭前清理
window.addEventListener('beforeunload', () => {
    app.stop();
});
