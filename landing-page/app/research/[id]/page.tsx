import { notFound } from 'next/navigation';

interface PageProps {
  params: { id: string };
}

export default async function ResearchPage({ params }: PageProps) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aisatisfy.me';

  try {
    const res = await fetch(`${apiUrl}/files/${params.id}.html`, {
      cache: 'no-store',
    });

    if (!res.ok) {
      return notFound();
    }

    const html = await res.text();

    return (
      <div className="min-h-screen">
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    );
  } catch (error) {
    console.error('Error fetching research HTML:', error);
    return notFound();
  }
}

export async function generateMetadata({ params }: PageProps) {
  return {
    title: `Research: ${params.id.replace(/_/g, ' ')} - AI Satisfy`,
    description: `AI Research on ${params.id.replace(/_/g, ' ')}`,
  };
}
