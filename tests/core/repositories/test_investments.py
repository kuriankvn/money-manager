import unittest
import os
import tempfile
from datetime import date
from core.storage.init_db import init_database
from core.domain import Investment, InvestmentValueSnapshot, InvestmentPlan, InvestmentPlanInstance
from core.domain.base import InvestmentStatus, Frequency, InvestmentPlanStatus, InvestmentPlanInstanceStatus
from core.repositories import (
    InvestmentRepository,
    InvestmentValueSnapshotRepository,
    InvestmentPlanRepository,
    InvestmentPlanInstanceRepository
)


class TestInvestmentRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        self.repo = InvestmentRepository()
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        investment = Investment(
            uid='inv-1',
            name='Stock Portfolio',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        uid = self.repo.create(investment)
        self.assertEqual(uid, 'inv-1')
    
    def test_get_by_id(self) -> None:
        investment = Investment(
            uid='inv-2',
            name='Mutual Fund',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.repo.create(investment)
        retrieved = self.repo.get_by_id('inv-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        inv1 = Investment(uid='inv-3', name='Investment 1', start_date=date(2024, 1, 1),
                         status=InvestmentStatus.ACTIVE)
        inv2 = Investment(uid='inv-4', name='Investment 2', start_date=date(2024, 1, 1),
                         status=InvestmentStatus.ACTIVE)
        self.repo.create(inv1)
        self.repo.create(inv2)
        investments = self.repo.get_all()
        self.assertEqual(len(investments), 2)
    
    def test_update(self) -> None:
        investment = Investment(
            uid='inv-5',
            name='Original',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.repo.create(investment)
        investment.status = InvestmentStatus.CLOSED
        result = self.repo.update(investment)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        investment = Investment(
            uid='inv-6',
            name='Delete Me',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.repo.create(investment)
        result = self.repo.delete('inv-6')
        self.assertTrue(result)


class TestInvestmentValueSnapshotRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        
        self.inv_repo = InvestmentRepository()
        self.repo = InvestmentValueSnapshotRepository()
        
        self.investment = Investment(
            uid='inv-1',
            name='Stock Portfolio',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.inv_repo.create(self.investment)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        snapshot = InvestmentValueSnapshot(
            uid='snap-1',
            investment_id=self.investment.uid,
            date=date(2024, 1, 15),
            current_value=10000.0
        )
        uid = self.repo.create(snapshot)
        self.assertEqual(uid, 'snap-1')
    
    def test_get_by_id(self) -> None:
        snapshot = InvestmentValueSnapshot(
            uid='snap-2',
            investment_id=self.investment.uid,
            date=date(2024, 1, 15),
            current_value=10000.0
        )
        self.repo.create(snapshot)
        retrieved = self.repo.get_by_id('snap-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        snap1 = InvestmentValueSnapshot(uid='snap-3', investment_id=self.investment.uid,
                                       date=date(2024, 1, 15), current_value=10000.0)
        snap2 = InvestmentValueSnapshot(uid='snap-4', investment_id=self.investment.uid,
                                       date=date(2024, 2, 15), current_value=11000.0)
        self.repo.create(snap1)
        self.repo.create(snap2)
        snapshots = self.repo.get_all()
        self.assertEqual(len(snapshots), 2)
    
    def test_update(self) -> None:
        snapshot = InvestmentValueSnapshot(
            uid='snap-5',
            investment_id=self.investment.uid,
            date=date(2024, 1, 15),
            current_value=10000.0
        )
        self.repo.create(snapshot)
        snapshot.current_value = 12000.0
        result = self.repo.update(snapshot)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        snapshot = InvestmentValueSnapshot(
            uid='snap-6',
            investment_id=self.investment.uid,
            date=date(2024, 1, 15),
            current_value=10000.0
        )
        self.repo.create(snapshot)
        result = self.repo.delete('snap-6')
        self.assertTrue(result)


class TestInvestmentPlanRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        
        self.inv_repo = InvestmentRepository()
        self.repo = InvestmentPlanRepository()
        
        self.investment = Investment(
            uid='inv-1',
            name='Stock Portfolio',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.inv_repo.create(self.investment)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        plan = InvestmentPlan(
            uid='plan-1',
            investment_id=self.investment.uid,
            amount=1000.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            status=InvestmentPlanStatus.ACTIVE
        )
        uid = self.repo.create(plan)
        self.assertEqual(uid, 'plan-1')
    
    def test_get_by_id(self) -> None:
        plan = InvestmentPlan(
            uid='plan-2',
            investment_id=self.investment.uid,
            amount=1000.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            status=InvestmentPlanStatus.ACTIVE
        )
        self.repo.create(plan)
        retrieved = self.repo.get_by_id('plan-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        plan1 = InvestmentPlan(uid='plan-3', investment_id=self.investment.uid,
                              amount=1000.0, frequency=Frequency.MONTHLY,
                              interval=1, status=InvestmentPlanStatus.ACTIVE)
        plan2 = InvestmentPlan(uid='plan-4', investment_id=self.investment.uid,
                              amount=5000.0, frequency=Frequency.YEARLY,
                              interval=1, status=InvestmentPlanStatus.ACTIVE)
        self.repo.create(plan1)
        self.repo.create(plan2)
        plans = self.repo.get_all()
        self.assertEqual(len(plans), 2)
    
    def test_update(self) -> None:
        plan = InvestmentPlan(
            uid='plan-5',
            investment_id=self.investment.uid,
            amount=1000.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            status=InvestmentPlanStatus.ACTIVE
        )
        self.repo.create(plan)
        plan.amount = 1500.0
        result = self.repo.update(plan)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        plan = InvestmentPlan(
            uid='plan-6',
            investment_id=self.investment.uid,
            amount=1000.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            status=InvestmentPlanStatus.ACTIVE
        )
        self.repo.create(plan)
        result = self.repo.delete('plan-6')
        self.assertTrue(result)


class TestInvestmentPlanInstanceRepository(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        os.environ['MONEY_MANAGER_DB'] = self.test_db.name
        init_database()
        
        self.inv_repo = InvestmentRepository()
        self.plan_repo = InvestmentPlanRepository()
        self.repo = InvestmentPlanInstanceRepository()
        
        self.investment = Investment(
            uid='inv-1',
            name='Stock Portfolio',
            start_date=date(2024, 1, 1),
            status=InvestmentStatus.ACTIVE
        )
        self.inv_repo.create(self.investment)
        
        self.plan = InvestmentPlan(
            uid='plan-1',
            investment_id=self.investment.uid,
            amount=1000.0,
            frequency=Frequency.MONTHLY,
            interval=1,
            status=InvestmentPlanStatus.ACTIVE
        )
        self.plan_repo.create(self.plan)
    
    def tearDown(self) -> None:
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
        if 'MONEY_MANAGER_DB' in os.environ:
            del os.environ['MONEY_MANAGER_DB']
    
    def test_create(self) -> None:
        instance = InvestmentPlanInstance(
            uid='inst-1',
            investment_plan_id=self.plan.uid,
            amount=1000.0,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=InvestmentPlanInstanceStatus.PLANNED
        )
        uid = self.repo.create(instance)
        self.assertEqual(uid, 'inst-1')
    
    def test_get_by_id(self) -> None:
        instance = InvestmentPlanInstance(
            uid='inst-2',
            investment_plan_id=self.plan.uid,
            amount=1000.0,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=InvestmentPlanInstanceStatus.PLANNED
        )
        self.repo.create(instance)
        retrieved = self.repo.get_by_id('inst-2')
        self.assertIsNotNone(retrieved)
    
    def test_get_all(self) -> None:
        inst1 = InvestmentPlanInstance(uid='inst-3', investment_plan_id=self.plan.uid,
                                      amount=1000.0, due_date=date(2024, 1, 15),
                                      transaction_id=None, status=InvestmentPlanInstanceStatus.PLANNED)
        inst2 = InvestmentPlanInstance(uid='inst-4', investment_plan_id=self.plan.uid,
                                      amount=1000.0, due_date=date(2024, 2, 15),
                                      transaction_id=None, status=InvestmentPlanInstanceStatus.PLANNED)
        self.repo.create(inst1)
        self.repo.create(inst2)
        instances = self.repo.get_all()
        self.assertEqual(len(instances), 2)
    
    def test_update(self) -> None:
        instance = InvestmentPlanInstance(
            uid='inst-5',
            investment_plan_id=self.plan.uid,
            amount=1000.0,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=InvestmentPlanInstanceStatus.PLANNED
        )
        self.repo.create(instance)
        instance.status = InvestmentPlanInstanceStatus.EXECUTED
        result = self.repo.update(instance)
        self.assertTrue(result)
    
    def test_delete(self) -> None:
        instance = InvestmentPlanInstance(
            uid='inst-6',
            investment_plan_id=self.plan.uid,
            amount=1000.0,
            due_date=date(2024, 1, 15),
            transaction_id=None,
            status=InvestmentPlanInstanceStatus.PLANNED
        )
        self.repo.create(instance)
        result = self.repo.delete('inst-6')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
