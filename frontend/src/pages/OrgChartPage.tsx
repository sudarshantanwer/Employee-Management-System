import { useEffect, useState } from 'react';
import { getErrorMessage } from '../api/client';
import { fetchOrgChart } from '../api/employees';
import { Alert, Badge, Card, Spinner } from '../components/ui';
import { OrgChartNode } from '../types';

function OrgNode({ node, depth = 0 }: { node: OrgChartNode; depth?: number }) {
  return (
    <div className={depth > 0 ? 'ml-6 mt-3 border-l-2 border-brand-200 pl-4' : ''}>
      <div className="inline-block rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm">
        <p className="font-semibold text-slate-900">{node.name}</p>
        <p className="text-sm text-slate-600">{node.designation}</p>
        <Badge color="blue">{node.department}</Badge>
        {node.children.length > 0 && (
          <p className="mt-1 text-xs text-slate-500">{node.children.length} direct report(s)</p>
        )}
      </div>
      {node.children.map((child) => (
        <OrgNode key={child.id} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export function OrgChartPage() {
  const [roots, setRoots] = useState<OrgChartNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrgChart()
      .then(setRoots)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Organization Chart</h1>
        <p className="text-sm text-slate-600">Reporting hierarchy based on manager assignments</p>
      </div>

      {error && <Alert message={error} />}

      <Card className="p-6">
        {loading ? (
          <Spinner />
        ) : roots.length === 0 ? (
          <p className="text-center text-slate-500">No employees to display</p>
        ) : (
          <div className="space-y-6">
            {roots.map((root) => (
              <OrgNode key={root.id} node={root} />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
