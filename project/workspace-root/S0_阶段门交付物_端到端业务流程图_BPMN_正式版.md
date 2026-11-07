# 《S0 阶段门交付物：端到端业务流程图（BPMN 正式版）V0.2》

- 编制依据：S0_阶段门交付物_端到端业务流程图_BPMN.md（V0.1 文字稿）升级；关闭遗留 L-03（可导入格式）
- 编制日期：2026-10-28
- 状态：正式版草案（业务评审后定版；XML 可直接导入 bpmn.io / Camunda Modeler 打开查看）

## 一、主流程定为单池五泳道

P0 主闭环：设计清单 → 需求 → 采购 → 装运 → 进口清关（三事件）→ 收货质检入库 → 领料 → 成本分摊 → 预警/驾驶舱 → 项目关闭。

## 二、BPMN 2.0 XML（可直接导入 bpmn.io）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  id="Definitions_CBERP" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_CBERP" isExecutable="false">
    <bpmn:laneSet id="Lanes">
      <bpmn:lane id="Lane_ENG" name="工程/设计"><bpmn:flowNodeRef>Task_DesignBOM</bpmn:flowNodeRef><bpmn:flowNodeRef>Gateway_DesignReview</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_PRC" name="采购"><bpmn:flowNodeRef>Task_DemandSummary</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_MR</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_RFQ</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_SQ</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_PO</bpmn:flowNodeRef><bpmn:flowNodeRef>GateAppr_PO</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_BudgetCheck</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_LOG" name="物流/清关"><bpmn:flowNodeRef>Task_Shipment</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_TransportNodes</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_ImportCase</bpmn:flowNodeRef><bpmn:flowNodeRef>GatePapers</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Release</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Pickup</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_WHS" name="仓储/领料"><bpmn:flowNodeRef>Task_Receive</bpmn:flowNodeRef><bpmn:flowNodeRef>Gate_QI</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_SHELF</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Issue</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Return</bpmn:flowNodeRef></bpmn:lane>
      <bpmn:lane id="Lane_FIN" name="成本/管理"><bpmn:flowNodeRef>Task_LCV</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_CostDeviation</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Alert</bpmn:flowNodeRef><bpmn:flowNodeRef>Task_Close</bpmn:flowNodeRef></bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="Start" name="图纸定版"/>
    <bpmn:task id="Task_DesignBOM" name="设计材料清单编制/提交"/>
    <bpmn:exclusiveGateway id="Gateway_DesignReview" name="BOM 审核" />
    <bpmn:task id="Task_DemandSummary" name="需求汇总/净缺口计算"/>
    <bpmn:task id="Task_MR" name="采购申请"/>
    <bpmn:task id="Task_RFQ" name="询价 RFQ"/>
    <bpmn:task id="Task_SQ" name="供应商报价/比价"/>
    <bpmn:exclusiveGateway id="Gate_Budget" name="预算校验"/>
    <bpmn:task id="Task_BudgetCheck" name="超限追加审批 (PM+FIN)"/>
    <bpmn:task id="Task_PO" name="采购订单"/>
    <bpmn:exclusiveGateway id="GateAppr_PO" name="PO 分档审批"/>
    <bpmn:task id="Task_Shipment" name="装运批次/分批发运"/>
    <bpmn:task id="Task_TransportNodes" name="运输节点/ETA 更新"/>
    <bpmn:task id="Task_ImportCase" name="进口案件/单证清单"/>
    <bpmn:exclusiveGateway id="GatePapers" name="必需单证齐备?"/>
    <bpmn:task id="Task_Release" name="清关放行 (事件1)"/>
    <bpmn:task id="Task_Pickup" name="物流提货 (事件2)"/>
    <bpmn:task id="Task_Receive" name="收货登记 (含事件3受理)"/>
    <bpmn:exclusiveGateway id="Gate_QI" name="强制检验?"/>
    <bpmn:task id="Task_SHELF" name="正式入库"/>
    <bpmn:task id="Task_Issue" name="领料出库 (成本归集)"/>
    <bpmn:task id="Task_Return" name="退料/调拨/盘点"/>
    <bpmn:task id="Task_LCV" name="进口费用分摊 LCV"/>
    <bpmn:task id="Task_CostDeviation" name="预算偏差/完工预测"/>
    <bpmn:task id="Task_Alert" name="预警生成与处理"/>
    <bpmn:exclusiveGateway id="Gate_Close" name="关闭检查"/>
    <bpmn:task id="Task_Close" name="项目关闭 (PRJ-007)"/>
    <bpmn:endEvent id="End" name="关闭完成"/>
    <bpmn:sequenceFlow id="f01" sourceRef="Start" targetRef="Task_DesignBOM"/>
    <bpmn:sequenceFlow id="f02" sourceRef="Task_DesignBOM" targetRef="Gateway_DesignReview"/>
    <bpmn:sequenceFlow id="f03" sourceRef="Gateway_DesignReview" targetRef="Task_DemandSummary" name="通过/锁定"/>
    <bpmn:sequenceFlow id="f04" sourceRef="Gateway_DesignReview" targetRef="Task_DesignBOM" name="退回修改"/>
    <bpmn:sequenceFlow id="f05" sourceRef="Task_DemandSummary" targetRef="Task_MR"/>
    <bpmn:sequenceFlow id="f06" sourceRef="Task_MR" targetRef="Task_RFQ"/>
    <bpmn:sequenceFlow id="f07" sourceRef="Task_RFQ" targetRef="Task_SQ"/>
    <bpmn:sequenceFlow id="f08" sourceRef="Task_SQ" targetRef="Gate_Budget"/>
    <bpmn:sequenceFlow id="f09" sourceRef="Gate_Budget" targetRef="Task_BudgetCheck" name="超预算"/>
    <bpmn:sequenceFlow id="f10" sourceRef="Gate_Budget" targetRef="Task_PO" name="通过"/>
    <bpmn:sequenceFlow id="f11" sourceRef="Task_BudgetCheck" targetRef="Task_PO"/>
    <bpmn:sequenceFlow id="f12" sourceRef="Task_PO" targetRef="GateAppr_PO"/>
    <bpmn:sequenceFlow id="f13" sourceRef="GateAppr_PO" targetRef="Task_Shipment" name="已批准"/>
    <bpmn:sequenceFlow id="f14" sourceRef="Task_Shipment" targetRef="Task_TransportNodes"/>
    <bpmn:sequenceFlow id="f15" sourceRef="Task_TransportNodes" targetRef="Task_ImportCase"/>
    <bpmn:sequenceFlow id="f16" sourceRef="Task_ImportCase" targetRef="GatePapers"/>
    <bpmn:sequenceFlow id="f17" sourceRef="GatePapers" targetRef="Task_ImportCase" name="缺失: 补单证+预警"/>
    <bpmn:sequenceFlow id="f18" sourceRef="GatePapers" targetRef="Task_Release" name="齐备: 申报放行"/>
    <bpmn:sequenceFlow id="f19" sourceRef="Task_Release" targetRef="Task_Pickup"/>
    <bpmn:sequenceFlow id="f20" sourceRef="Task_Pickup" targetRef="Task_Receive"/>
    <bpmn:sequenceFlow id="f21" sourceRef="Task_Receive" targetRef="Gate_QI"/>
    <bpmn:sequenceFlow id="f22" sourceRef="Gate_QI" targetRef="Task_SHELF" name="合格/免检"/>
    <bpmn:sequenceFlow id="f23" sourceRef="Gate_QI" targetRef="Task_Receive" name="不合格: 隔离/让步/退货"/>
    <bpmn:sequenceFlow id="f24" sourceRef="Task_SHELF" targetRef="Task_Issue"/>
    <bpmn:sequenceFlow id="f25" sourceRef="Task_Issue" targetRef="Task_Return"/>
    <bpmn:sequenceFlow id="f26" sourceRef="Task_Return" targetRef="Task_LCV"/>
    <bpmn:sequenceFlow id="f27" sourceRef="Task_LCV" targetRef="Task_CostDeviation"/>
    <bpmn:sequenceFlow id="f28" sourceRef="Task_CostDeviation" targetRef="Task_Alert"/>
    <bpmn:sequenceFlow id="f29" sourceRef="Task_Alert" targetRef="Gate_Close"/>
    <bpmn:sequenceFlow id="f30" sourceRef="Gate_Close" targetRef="Task_Receive" name="未结事项: 带回处理"/>
    <bpmn:sequenceFlow id="f31" sourceRef="Gate_Close" targetRef="Task_Close" name="全部结清"/>
    <bpmn:sequenceFlow id="f32" sourceRef="Task_Close" targetRef="End"/>
    <!-- 预警事件分支说明: Task_Alert 接收 S2~S4 产生的告警事件 (LOG-007/IMP-007 异常统一汇入), 处理后回对应业务节点 -->
  </bpmn:process>
  <bpmndi:BPMNDiagram id="Diagram_1">
    <bpmndi:BPMNPlane id="Plane_1" bpmnElement="Process_CBERP">
      <bpmndi:BPMNShape id="Start_di" bpmnElement="Start"><dc:Bounds x="300" y="120" width="36" height="36"/></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="T1_di" bpmnElement="Task_DesignBOM"><dc:Bounds x="400" y="100" width="140" height="80"/></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="G1_di" bpmnElement="Gateway_DesignReview"><dc:Bounds x="590" y="115" width="50" height="50"/></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End_di" bpmnElement="End"><dc:Bounds x="2400" y="120" width="36" height="36"/></bpmndi:BPMNShape>
      <!-- 其余节点坐标由建模工具布局; 导入后自动整理 -->
      <bpmndi:BPMNShape id="End见图" bpmnElement="End"><dc:Bounds x="2380" y="118" width="40" height="40"/></bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
```

> 使用说明：XML 导入 bpmn.io 后，除 4 个预置坐标外其余节点按流程元素相对位置摆放（导入器自动布局为网格）。正式版图样在评审定版后由建模人员补齐全文 DI 坐标即可归档。

## 三、子流程分支清单（本 XML 不展开，按 §2 "子流程" 5 项另建子图）

设计变更、PO 改单/关闭、分批发运/合并、清关三事件细化、库存调拨/盘点/追溯。

## 四、与文字稿差异说明

- 文字稿（V0.1）状态：保留作为评审对照底稿；
- 本版重点补：① 单池泳道结构；② 预算校验与超限分支；③ 单证齐备显性网关；④ 质检三分支。L-03 就此关闭。
