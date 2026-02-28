"""
性能基准测试 - Agent Collaboration
"""
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acp_extensions import NegotiationManager, VotingManager, DelegationManager, MessageBus, VoteType


def benchmark_collaboration_performance():
    """基准测试：多智能体协作性能"""
    print("=" * 60)
    print("多智能体协作性能基准测试")
    print("=" * 60)
    
    # 创建消息总线
    message_bus = MessageBus()
    
    # 测试1: 协商管理器初始化
    start = time.time()
    negotiator = NegotiationManager(message_bus)
    init_time = time.time() - start
    print(f"\n1. 协商管理器初始化")
    print(f"   耗时: {init_time:.4f}s")
    print(f"   状态: {'✅ 通过' if init_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试2: 投票管理器性能
    start = time.time()
    voting = VotingManager(message_bus)
    voting_time = time.time() - start
    print(f"\n2. 投票管理器初始化")
    print(f"   耗时: {voting_time:.4f}s")
    print(f"   状态: {'✅ 通过' if voting_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试3: 委托管理器性能
    start = time.time()
    delegation = DelegationManager(message_bus)
    deleg_time = time.time() - start
    print(f"\n3. 委托管理器初始化")
    print(f"   耗时: {deleg_time:.4f}s")
    print(f"   状态: {'✅ 通过' if deleg_time < 0.1 else '⚠️ 较慢'}")
    
    # 测试4: 协商提议性能
    start = time.time()
    for i in range(100):
        negotiator.create_proposal(
            proposer=f"agent-{i % 10}",
            proposal_type=f"topic-{i}",
            content={"param": i},
            conditions={"timeout": 60}
        )
    propose_time = time.time() - start
    print(f"\n4. 协商提议性能 (100次)")
    print(f"   耗时: {propose_time:.4f}s")
    print(f"   状态: {'✅ 通过' if propose_time < 0.5 else '⚠️ 较慢'}")
    
    # 测试5: 投票创建性能
    start = time.time()
    for i in range(50):
        voting.create_vote(
            topic=f"vote-{i}",
            vote_type=VoteType.MAJORITY,
            options=["option-a", "option-b", "option-c"],
            eligible_voters=[f"agent-{j}" for j in range(5)],
            duration_seconds=300
        )
    vote_time = time.time() - start
    print(f"\n5. 投票创建性能 (50次)")
    print(f"   耗时: {vote_time:.4f}s")
    print(f"   状态: {'✅ 通过' if vote_time < 0.5 else '⚠️ 较慢'}")
    
    # 测试6: 委托创建性能
    start = time.time()
    for i in range(50):
        delegation.create_delegation(
            delegator=f"delegator-{i % 10}",
            delegatee=f"delegate-{i % 5}",
            scope=["all"],
            permissions=["read", "write"],
            duration_seconds=3600
        )
    deleg_create_time = time.time() - start
    print(f"\n6. 委托创建性能 (50次)")
    print(f"   耗时: {deleg_create_time:.4f}s")
    print(f"   状态: {'✅ 通过' if deleg_create_time < 0.5 else '⚠️ 较慢'}")
    
    print("\n" + "=" * 60)
    print("性能基准测试完成")
    print("=" * 60)
    
    return {
        "init_time": init_time,
        "voting_time": voting_time,
        "deleg_time": deleg_time,
        "propose_time": propose_time,
        "vote_time": vote_time,
        "deleg_create_time": deleg_create_time
    }


if __name__ == "__main__":
    benchmark_collaboration_performance()
