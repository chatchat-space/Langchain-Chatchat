export default {
  dbV1: {
    action: {
      clearDB: '清空本地数据',
      downloadBackup: '下载数据备份',
      reUpgrade: '重新升级',
      start: '开始使用',
      upgrade: '一键升级',
    },
    clear: {
      confirm: '即将清空本地数据（全局设置不受影响），请确认你已经下载了数据备份。',
    },
    description:
      '在新版本中，ChatChat 的数据存储有了巨大的飞跃。因此我们要对旧版数据进行升级，进而为你带来更好的使用体验。',
    features: {
      capability: {
        desc: '基于 IndexedDB 技术，足以装下你一生的会话消息',
        title: '大容量',
      },
      performance: {
        desc: '百万条消息自动索引，检索查询毫秒级响应',
        title: '高性能',
      },
      use: {
        desc: '支持标题、描述、标签、消息内容乃至翻译文本检索，日常搜索效率大大提升',
        title: '更易用',
      },
    },
    title: 'ChatChat 数据进化',
    upgrade: {
      error: {
        subTitle:
          '非常抱歉，数据库升级过程发生异常。请尝试以下方案：A. 清空本地数据后，重新导入备份数据； B.点击 「重新升级」按钮。<br><br> 如仍然出错，请 <1>提交问题</1> ，我们将会第一时间帮你排查',
        title: '数据库升级失败',
      },
      success: {
        subTitle: 'ChatChat 的数据库已经升级到最新版本，立即开始体验吧',
        title: '数据库升级成功',
      },
    },
    upgradeTip: '升级大致需要 10~20 秒，升级过程中请不要关闭 ChatChat',
  },
  migrateError: {
    missVersion: '导入数据缺少版本号，请检查文件后重试',
    noMigration: '没有找到当前版本对应的迁移方案，请检查版本号后重试。如仍有问题请提交问题反馈',
  },
};
